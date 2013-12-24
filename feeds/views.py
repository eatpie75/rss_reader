import json
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from pytz import timezone
from .forms import AddFeedForm
from .models import Feed, Article, UserArticleInfo, UserFeedSubscription, UserFeedCache, recalculate_user_cache
from .utils import check_feed


class DateEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.isoformat()
		return json.JSONEncoder.default(self, obj)


@login_required
def mark_all_read(request, feed):
	feed=int(feed)
	if feed!=0:
		feed=Feed.objects.get(pk=feed)
		UserArticleInfo.objects.filter(user=request.user, feed=feed, read=False).update(read=True, date_read=timezone('utc').localize(datetime.utcnow()))
		unread_count=UserFeedCache.objects.get(user=request.user, feed=feed).recalculate().unread
		data=[{'feed':0, 'count':UserArticleInfo.objects.filter(user=request.user, read=False).count()}, {'feed':feed.pk, 'count':unread_count}]
	else:
		UserArticleInfo.objects.filter(user=request.user, read=False).update(read=True, date_read=timezone('utc').localize(datetime.utcnow()))
		unread_count=recalculate_user_cache(request.user.pk)
		data=[{'feed':0, 'count':unread_count}]
	return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def mark_read(request, article):
	article=int(article)
	article=UserArticleInfo.objects.get(user=request.user, article=article)
	if not article.read:
		article.read=True
		article.date_read=timezone('utc').localize(datetime.utcnow())
		article.save()
		feed_unread=UserFeedCache.objects.get(user=request.user, feed=article.feed).sub()
		unread_count=UserArticleInfo.objects.filter(user=request.user, read=False).count()
		data=[{'feed':0, 'count':unread_count}, {'feed':article.feed.pk, 'count':feed_unread}]
	else:
		data=[]
	return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def mark_unread(request, article):
	article=int(article)
	article=UserArticleInfo.objects.get(user=request.user, article=article)
	if article.read:
		article.read=False
		article.date_read=None
		article.save()
		feed_unread=UserFeedCache.objects.get(user=request.user, feed=article.feed).add()
		unread_count=UserArticleInfo.objects.filter(user=request.user, read=False).count()
		data=[{'feed':0, 'count':unread_count}, {'feed':article.feed.pk, 'count':feed_unread}]
	else:
		data=[]
	return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def refresh_feed(request, feed):
	feed=int(feed)
	data=[]
	if feed!=0:
		feed=Feed.objects.get(pk=feed)
		feed.update()
		data.append({'feed':feed.pk, 'count':UserFeedCache.objects.get(user=request.user, feed=feed).unread})
	else:
		new_articles=0
		for feed in Feed.objects.filter(last_updated__lt=datetime.now(timezone('utc')) - timedelta(minutes=10)):
			new_articles+=feed.update()
			data.append({'feed':feed.pk, 'count':UserFeedCache.objects.get(user=request.user, feed=feed).unread})
		print('{} new article(s)'.format(new_articles))
	unread_count=UserArticleInfo.objects.filter(user=request.user, read=False).count()
	data.append({'feed':0, 'count':unread_count})
	return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def view_article(request, article):
	article=UserArticleInfo.objects.filter(user=request.user, article=article).select_related('article__content')
	return HttpResponse(json.dumps(article.values('article__content')[0], cls=DateEncoder), content_type='application/json')


@login_required
def view_feed_list(request):
	user_feeds=UserFeedSubscription.objects.filter(user=request.user).select_related('feed__id', 'feed__title', 'feed__success', 'feed__last_error')
	total_unread_count=UserFeedCache.objects.filter(user=request.user).aggregate(Sum('unread'))['unread__sum']
	individual_unread_count={}
	for a in UserFeedCache.objects.filter(user=request.user).only('feed__id', 'unread'):
		individual_unread_count[a.feed_id]=a.unread
	data={'total_unread_count':total_unread_count}
	feed_list=[]
	for user_feed in user_feeds:
		feed_list.append({
			'pk':user_feed.feed.id,
			'title':user_feed.feed.title,
			'success':user_feed.feed.success,
			'last_error':user_feed.feed.last_error,
			'unread':individual_unread_count[user_feed.feed.id]
		})
	data['feed_list']=feed_list
	return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json')
	# return render_to_response('blank.html.j2', {'a':json.dumps(data, cls=DateEncoder)})


@login_required
def view_feed_articles(request, feed):
	feed=int(feed)
	context=RequestContext(request)

	if feed!=0:
		feed=Feed.objects.get(pk=feed)
		articles=UserArticleInfo.objects.filter(user=request.user, feed=feed)
		if 'all' not in request.GET or request.GET['all']=='false':
			articles=articles.filter(read=False)
	else:
		articles=UserArticleInfo.objects.filter(user=request.user)
		if 'all' not in request.GET or request.GET['all']=='false':
			articles=articles.filter(read=False)

	if 'last_article' in request.GET:
		last_article=float(request.GET['last_article']) / 1000.0
		last_article=datetime.fromtimestamp(last_article)
		articles=articles.filter(article__date_published__lt=last_article)

	if 'limit' in request.GET:
		limit=min(int(request.GET['limit']), 50)
	else:
		limit=50

	articles=articles.select_related('article', 'feed__pk', 'feed__title', 'feed__get_feed_image', 'user__pk')

	data=[]
	for user_article in articles[:limit]:
		tmp={
			'pk':user_article.pk,
			'user':user_article.user.pk,
			'feed':{
				'pk':user_article.feed.pk,
				'title':user_article.feed.title,
				'image':user_article.feed.get_feed_image if user_article.feed.get_feed_image is not None else context['STATIC_URL'] + 'img/rss.png'
			},
			'article':{
				'pk':user_article.article.pk,
				'title':user_article.article.title,
				'author':user_article.article.author,
				'date_published':user_article.article.date_published,
				'date_published_relative':user_article.article.date_published_relative,
				'date_added':user_article.article.date_added,
				# 'description':user_article.article.description,
				# 'content':user_article.article.content,
				'url':user_article.article.url
			},
			'read':user_article.read,
			'date_read':user_article.date_read
		}
		data.append(tmp)
	return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json')
	# return render_to_response('blank.html.j2', {'a':json.dumps(data, cls=DateEncoder)}, context)


@login_required
def add_feed(request):
	if request.method=='POST':
		form=AddFeedForm(request.POST)
		if form.is_valid():
			feed=check_feed(form.cleaned_data['url'])
			if feed[0] is not None:
				# data={'error':str(feed[0])}
				data={'error':'Error fetching feed.'}
			else:
				if type(feed[1])!=int:
					feed=Feed(feed_url=form.cleaned_data['url'])
					feed.save()
				elif type(feed[1])==int:
					feed=Feed.objects.get(pk=feed[1])
					if feed.enabled is False:
						feed.enabled=True
					if feed.needs_update:
						feed.update()
				UserFeedSubscription(user=request.user, feed=feed).save()
				tmp=[]
				for article in Article.objects.filter(feed=feed.pk).only('pk')[:25]:
					tmp.append(UserArticleInfo(user=request.user, feed=feed, article=article))
				UserArticleInfo.objects.bulk_create(tmp)
				del tmp
				UserFeedCache(user=request.user, feed=feed).recalculate()

				data={
					'pk':feed.pk,
					'enabled':feed.enabled,
					'success':feed.success,
					'title':feed.title,
					'site_url':feed.site_url,
					'image':feed.get_feed_image
				}
		else:
			data={'error':'Input a valid url.'}
	else:
		data={'error':''}
	return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json')
