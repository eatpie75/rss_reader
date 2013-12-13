from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template import RequestContext
from models import Feed, UserArticleInfo, UserFeedCache, recalculate_user_cache
from pytz import timezone
import json


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
	article=UserArticleInfo.objects.get(article=article)
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
def view_feed_articles(request, feed):
	feed=int(feed)
	if feed!=0:
		feed=Feed.objects.get(pk=feed)
		articles=UserArticleInfo.objects.filter(user=request.user, feed=feed).select_related('article', 'feed__title', 'feed__get_image')
		if 'all' not in request.GET:
			articles=articles.filter(read=False)
	else:
		articles=UserArticleInfo.objects.filter(user=request.user).select_related('article', 'feed__title', 'feed__get_image')
		if 'all' not in request.GET:
			articles=articles.filter(read=False)
	return render_to_response('includes/article_list.html.j2', {'articles':articles[:50]}, RequestContext(request))
