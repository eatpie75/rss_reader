from coffin.shortcuts import render_to_response
from django.template import RequestContext
from feeds.models import Feed, Article


def index(request):
	feeds=Feed.objects.all()
	articles=Article.objects.filter(read=False)[:50]
	unread_count=Article.objects.filter(read=False).count()
	return render_to_response('index.html.j2', {'feeds':feeds, 'articles':articles, 'unread_count':unread_count}, RequestContext(request))
