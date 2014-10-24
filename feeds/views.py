import json
import utils as feed_utils
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.http import HttpResponse
# from django.shortcuts import render_to_response
# from django.template import RequestContext
from pytz import timezone
from .forms import AddFeedForm, EditFeedForm
from .models import Feed, Article, UserArticleInfo, UserFeedSubscription, UserFeedCache, recalculate_user_cache, Category

import logging
logger=logging.getLogger(__name__)


@login_required
def feed_info(request, feed):
	feed=int(feed)
	user_feed=UserFeedSubscription.objects.get(user=request.user, pk=feed)
	data=user_feed.get_all_info()
	return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


@login_required
def new_articles(request, feed):
	feed=int(feed)
	newest_article=datetime.strptime(request.GET['newest_article'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone('utc'), microsecond=999999)
	# print(newest_article, UserArticleInfo.objects.filter(user=request.user, read=False).latest('article__date_added').article.date_added)
	data={}

	if feed!=0:
		feed=UserFeedSubscription.objects.get(pk=feed)
		data['new_articles']=UserArticleInfo.objects.filter(user=request.user, feed=feed, read=False, article__date_added__gt=newest_article).exists()
	else:
		data['new_articles']=UserArticleInfo.objects.filter(user=request.user, read=False, article__date_added__gt=newest_article).exists()

	return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
	# return render_to_response('blank.html.j2', {'a':json.dumps(data, cls=DjangoJSONEncoder)})


@login_required
def new_category_articles(request, category):
	category=int(category)
	newest_article=datetime.strptime(request.GET['newest_article'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone('utc'), microsecond=999999)
	# print(newest_article, UserArticleInfo.objects.filter(user=request.user, read=False).latest('article__date_added').article.date_added)
	data={}

	category=Category.objects.get(pk=category)
	data['new_articles']=UserArticleInfo.objects.filter(user=request.user, feed__category=category, read=False, article__date_added__gt=newest_article).exists()

	return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
	# return render_to_response('blank.html.j2', {'a':json.dumps(data, cls=DjangoJSONEncoder)})


@login_required
def mark_all_read(request, feed):
	feed=int(feed)
	newest_article=datetime.strptime(request.GET['newest_article'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone('utc'), microsecond=999999)
	if feed!=0:
		feed=UserFeedSubscription.objects.get(pk=feed)
		UserArticleInfo.objects.filter(user=request.user, feed=feed, read=False, article__date_added__lt=newest_article).update(read=True, date_read=timezone('utc').localize(datetime.utcnow()))
		unread_count=UserFeedCache.objects.get(user=request.user, feed=feed).recalculate().unread
		data=[{'feed':0, 'unread':UserArticleInfo.objects.filter(user=request.user, read=False).count()}, {'feed':feed.pk, 'unread':unread_count}]
	else:
		UserArticleInfo.objects.filter(user=request.user, read=False, article__date_added__lt=newest_article).update(read=True, date_read=timezone('utc').localize(datetime.utcnow()))
		unread_count=recalculate_user_cache(request.user.pk)
		data=[{'feed':0, 'unread':max(unread_count, 0)}]
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
		data=[{'feed':0, 'unread':unread_count}, {'feed':article.feed.pk, 'unread':feed_unread}]
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
		data=[{'feed':0, 'unread':unread_count}, {'feed':article.feed.pk, 'unread':feed_unread}]
	else:
		data=[]
	return HttpResponse(json.dumps(data), content_type='application/json')
	# return render_to_response('blank.html.j2', {'a':json.dumps(data, cls=DjangoJSONEncoder)})


@login_required
def refresh_feed(request, feed):
	feed=int(feed)
	data=[]
	if feed!=0:
		feed=UserFeedSubscription.objects.get(pk=feed)
		feed.feed.update()
		data.append({'feed':feed.pk, 'unread':UserFeedCache.objects.get(user=request.user, feed=feed).unread})
	else:
		new_articles=0
		for user_feed in UserFeedSubscription.objects.filter(user=request.user, feed__last_updated__lt=datetime.now(timezone('utc')) - timedelta(minutes=10)):
			new_articles+=user_feed.feed.update()
			data.append({'feed':user_feed.pk, 'unread':UserFeedCache.objects.get(user=request.user, feed=user_feed).unread})
		logger.info('{} new article(s)'.format(new_articles))
	unread_count=UserArticleInfo.objects.filter(user=request.user, read=False).count()
	data.append({'feed':0, 'unread':unread_count})
	return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def view_article(request, article):
	article=UserArticleInfo.objects.filter(user=request.user, article=article).select_related('article__content')
	return HttpResponse(json.dumps(article.values('article__content')[0], cls=DjangoJSONEncoder), content_type='application/json')
	# return render_to_response('blank.html.j2', {'a':json.dumps(article.values('article__content')[0], cls=DjangoJSONEncoder)})


@login_required
def category_list(request):
	user_categories=Category.objects.filter(user=request.user).select_related('user__pk')
	data=[]
	for category in user_categories:
		data.append(category.get_basic_info())
	return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
	# return render_to_response('blank.html.j2', {'a':json.dumps(data, cls=DjangoJSONEncoder)})


@login_required
def view_feed_list(request):
	user_feeds=UserFeedSubscription.objects.filter(user=request.user).select_related('feed__feed__id', 'feed__title', 'feed__feed__success', 'feed__feed__last_error', 'category__id')
	total_unread_count=UserFeedCache.objects.filter(user=request.user).aggregate(Sum('unread'))['unread__sum']
	individual_unread_count={}
	for a in UserFeedCache.objects.filter(user=request.user).only('feed__id', 'unread'):
		individual_unread_count[a.feed.feed_id]=a.unread
	data={'total_unread_count':max(total_unread_count, 0)}
	feed_list=[]
	for user_feed in user_feeds:
		feed_list.append({
			'pk':user_feed.pk,
			'title':user_feed.title,
			'success':user_feed.feed.success,
			'last_error':user_feed.feed.last_error,
			'unread':individual_unread_count[user_feed.feed.id],
			'category':user_feed.category.id if user_feed.category is not None else None,
		})
	data['feed_list']=feed_list
	return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
	# return render_to_response('blank.html.j2', {'a':json.dumps(data, cls=DjangoJSONEncoder)})


@login_required
def view_feed_articles(request, feed):
	feed=int(feed)
	data={}

	if feed!=0:
		feed=UserFeedSubscription.objects.get(pk=feed)
		articles=UserArticleInfo.objects.filter(user=request.user, feed=feed)
		data['unread']=UserFeedCache.objects.filter(user=request.user, feed=feed).only('unread')[0].unread
		if request.GET.get('read', 'false')=='false':
			articles=articles.filter(read=False)
	else:
		articles=UserArticleInfo.objects.filter(user=request.user)
		data['unread']=UserFeedCache.objects.filter(user=request.user).aggregate(Sum('unread'))['unread__sum']
		if request.GET.get('read', 'false')=='false':
			articles=articles.filter(read=False)

	if 'last_article' in request.GET:
		last_article=float(request.GET['last_article']) / 1000.0
		last_article=datetime.fromtimestamp(last_article)
		articles=articles.filter(article__date_published__lt=last_article)

	if 'limit' in request.GET:
		limit=min(int(request.GET['limit']), 50)
	else:
		limit=50

	articles=articles.select_related('article', 'feed__feed__pk', 'feed__title', 'feed__feed__get_feed_image', 'user__pk')

	tmp=[]
	for user_article in articles[:limit]:
		tmp.append(user_article.get_basic_info())
	data['articles']=tmp
	data['unread']=max(data['unread'], 0)
	return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
	# return render_to_response('blank.html.j2', {'a':json.dumps(data, cls=DjangoJSONEncoder)})


@login_required
def view_category_articles(request, category):
	category=int(category)
	data={}

	category=Category.objects.get(pk=category)
	# feeds=UserFeedSubscription.objects.filter(user=request.user, category=category)
	articles=UserArticleInfo.objects.filter(user=request.user, feed__category=category)
	# data['unread']=UserFeedCache.objects.filter(user=request.user, feed__in=feeds).only('unread')[0].unread
	if request.GET.get('read', 'false')=='false':
		articles=articles.filter(read=False)

	if 'last_article' in request.GET:
		last_article=float(request.GET['last_article']) / 1000.0
		last_article=datetime.fromtimestamp(last_article)
		articles=articles.filter(article__date_published__lt=last_article)

	if 'limit' in request.GET:
		limit=min(int(request.GET['limit']), 50)
	else:
		limit=50

	articles=articles.select_related('article', 'feed__feed__pk', 'feed__title', 'feed__feed__get_feed_image', 'user__pk')

	tmp=[]
	for user_article in articles[:limit]:
		tmp.append(user_article.get_basic_info())
	data['articles']=tmp
	# data['unread']=max(data['unread'], 0)
	return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
	# return render_to_response('blank.html.j2', {'a':json.dumps(data, cls=DjangoJSONEncoder)})


@login_required
def add_feed(request):
	if request.method=='POST':
		form=AddFeedForm(request.POST)
		if form.is_valid():
			feed=feed_utils.check_feed(form.cleaned_data['url'])
			if feed[0] is not None:
				# data={'error':str(feed[0])}
				data={'error':'Error fetching feed.'}
			else:
				if type(feed[1])!=int:
					feed=Feed(feed_url=form.cleaned_data['url'])
					feed.save()
					logger.info('Created new feed: {}'.format(feed.feed_url))
				elif type(feed[1])==int:
					feed=Feed.objects.get(pk=feed[1])
					if feed.enabled is False:
						feed.enabled=True
					if feed.needs_update:
						feed.update()
				user_feed=UserFeedSubscription(user=request.user, feed=feed, title=feed.title)
				user_feed.save()
				tmp=[]
				for article in Article.objects.filter(feed=feed.pk).only('pk')[:25]:
					tmp.append(UserArticleInfo(user=request.user, feed=user_feed, article=article))
				UserArticleInfo.objects.bulk_create(tmp)
				del tmp
				UserFeedCache(user=request.user, feed=user_feed).recalculate()

				data=user_feed.get_basic_info()
		else:
			data={'error':'Input a valid url.'}
	else:
		data={'error':''}
	return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


@login_required
def edit_feed(request, feed):
	def finish(data):
		return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
	feed=int(feed)
	if request.method=='POST':
		form=EditFeedForm(request.POST)
		user_feed=UserFeedSubscription.objects.get(user=request.user, pk=feed)
		feed=Feed.objects.get(pk=user_feed.feed.pk)
		changes=False
		if form.is_valid():
			if form.cleaned_data['feed_url']!=user_feed.feed.feed_url:
				check=feed_utils.check_feed(form.cleaned_data['feed_url'], validity_check=False)
				if check[1] is not None and check[1]!=feed.pk:
					new_feed=Feed.objects.get(pk=check[1])
					tmp=[]
					for article in Article.objects.filter(feed=new_feed)[:10]:
						tmp.append(UserArticleInfo(user=request.user, feed=user_feed, article=article))
					UserArticleInfo.objects.bulk_create(tmp)
					del tmp
					user_feed.feed=new_feed
					user_feed.save()
				elif check[1]!=user_feed.feed.pk:
					valid=feed_utils.check_feed(form.cleaned_data['feed_url'], existence_check=False)
					if valid[0] is not None:
						return finish({'error':'Error fetching feed.'})
					else:
						feed.feed_url=form.cleaned_data['feed_url']
						changes=True
			if form.cleaned_data['site_url']!=feed.site_url:
				feed.site_url=form.cleaned_data['site_url']
				changes=True
			if form.cleaned_data['title']!=user_feed.title:
				user_feed.title=form.cleaned_data['title']
				user_feed.save()
			if form.cleaned_data['category']!=user_feed.category:
				user_feed.category=form.cleaned_data['category']
				user_feed.save()
			if changes:
				feed.save()
				feed.update()
			return finish(user_feed.get_basic_info())
		else:
			return finish({'form_errors':form.errors})
	else:
		return finish({'error':''})
