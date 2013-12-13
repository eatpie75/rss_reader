from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render_to_response
from django.template import RequestContext
from feeds.models import UserFeedSubscription, UserArticleInfo, UserFeedCache


@login_required
def index(request):
	user_feeds=UserFeedSubscription.objects.filter(user=request.user).select_related('feed')
	total_unread_count=UserFeedCache.objects.filter(user=request.user).aggregate(Sum('unread'))['unread__sum']
	individual_unread_count={}
	for a in UserFeedCache.objects.filter(user=request.user).only('feed__id', 'unread'):
		individual_unread_count[a.feed_id]=a.unread
	return render_to_response('index.html.j2', {'user_feeds':user_feeds, 'total_unread_count':total_unread_count, 'individual_unread_count':individual_unread_count}, RequestContext(request))
