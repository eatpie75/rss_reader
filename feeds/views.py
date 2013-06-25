from coffin.shortcuts import render_to_response
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template import RequestContext
from models import Feed, Article
from pytz import timezone
import json


class DateEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.isoformat()
		return json.JSONEncoder.default(self, obj)


def mark_all_read(request, feed):
	feed=int(feed)
	if feed!=0:
		feed=Feed.objects.get(pk=feed)
		Article.objects.filter(feed=feed, read=False).update(read=True)
	else:
		Article.objects.filter(read=False).update(read=True)
	unread_count=Article.objects.filter(read=False).count()
	data=[{'feed':0, 'count':unread_count}]
	return HttpResponse(json.dumps(data), mimetype='application/json')


def mark_read(request, article):
	article=int(article)
	article=Article.objects.get(pk=article)
	article.read=True
	article.save()
	feed_unread=Article.objects.filter(feed=article.feed, read=False).count()
	unread_count=Article.objects.filter(read=False).count()
	data=[{'feed':0, 'count':unread_count}, {'feed':article.feed.pk, 'count':feed_unread}]
	return HttpResponse(json.dumps(data), mimetype='application/json')


def mark_unread(request, article):
	article=int(article)
	article=Article.objects.get(pk=article)
	article.read=False
	article.save()
	feed_unread=Article.objects.filter(feed=article.feed, read=False).count()
	unread_count=Article.objects.filter(read=False).count()
	data=[{'feed':0, 'count':unread_count}, {'feed':article.feed.pk, 'count':feed_unread}]
	return HttpResponse(json.dumps(data), mimetype='application/json')


def refresh_feed(request, feed):
	feed=int(feed)
	data=[]
	if feed!=0:
		feed=Feed.objects.get(pk=feed)
		feed.update()
		data.append({'feed':feed.pk, 'count':feed.unread_count})
	else:
		new_articles=0
		for feed in Feed.objects.filter(last_updated__lt=datetime.now(timezone('utc'))-timedelta(minutes=10)):
			new_articles+=feed.update()
			data.append({'feed':feed.pk, 'count':feed.unread_count})
		print('{} new article(s)'.format(new_articles))
	unread_count=Article.objects.filter(read=False).count()
	data.append({'feed':0, 'count':unread_count})
	return HttpResponse(json.dumps(data), mimetype='application/json')


def view_article(request, article):
	article=Article.objects.filter(pk=article)
	return HttpResponse(json.dumps(article.values()[0], cls=DateEncoder), mimetype='application/json')


def view_feed_articles(request, feed):
	feed=int(feed)
	if feed!=0:
		feed=Feed.objects.get(pk=feed)
		articles=Article.objects.filter(feed=feed)
		if 'all' not in request.GET:
			articles=articles.filter(read=False)
	else:
		articles=Article.objects.all()
		if 'all' not in request.GET:
			articles=Article.objects.filter(read=False)
	return render_to_response('includes/article_list.html.j2', {'articles':articles[:50]}, RequestContext(request))
