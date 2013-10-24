from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from feeds.models import Feed, Article


@login_required
def index(request):
	feeds=Feed.objects.all()
	articles=Article.objects.all()
	if 'all' not in request.GET:
		articles=articles.filter(read=False)
	total_unread_count=Article.objects.filter(read=False).count()
	individual_unread_count={}
	for a in Article.objects.filter(read=False).only('feed__id'):
		a=a.feed_id
		if a not in individual_unread_count:
			individual_unread_count[a]=0
		individual_unread_count[a]+=1
	return render_to_response('index.html.j2', {'feeds':feeds, 'total_unread_count':total_unread_count, 'individual_unread_count':individual_unread_count}, RequestContext(request))
