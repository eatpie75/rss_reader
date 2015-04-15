import feeds.utils as feed_utils
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
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
	return JsonResponse(data, safe=False)


@login_required
def new_articles(request, feed):
	feed=int(feed)
	newest_article=datetime.strptime(request.GET['newest_article'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone('utc'), microsecond=999999)
	data={}

	if feed!=0:
		feed=UserFeedSubscription.objects.get(pk=feed)
		data['new_articles']=UserArticleInfo.objects.filter(user=request.user, feed=feed, read=False, article__date_added__gt=newest_article).exists()
	else:
		data['new_articles']=UserArticleInfo.objects.filter(user=request.user, read=False, article__date_added__gt=newest_article).exists()

	return JsonResponse(data, safe=False)


@login_required
def new_category_articles(request, category):
	category=int(category)
	newest_article=datetime.strptime(request.GET['newest_article'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone('utc'), microsecond=999999)
	data={}

	category=Category.objects.get(pk=category)
	data['new_articles']=UserArticleInfo.objects.filter(user=request.user, feed__category=category, read=False, article__date_added__gt=newest_article).exists()

	return JsonResponse(data, safe=False)


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
	return JsonResponse(data, safe=False)


@login_required
def mark_read(request, article):
	article=int(article)
	article=UserArticleInfo.objects.get(user=request.user, article=article)
	if not article.read:
		feed_unread=article.change_read_state(True)
		unread_count=UserArticleInfo.objects.filter(user=request.user, read=False).count()
		data=[{'feed':0, 'unread':unread_count}, {'feed':article.feed.pk, 'unread':feed_unread}]
	else:
		data=[]
	return JsonResponse(data, safe=False)


@login_required
def mark_unread(request, article):
	article=int(article)
	article=UserArticleInfo.objects.get(user=request.user, article=article)
	if article.read:
		article.change_read_state(False)
		feed_unread=UserFeedCache.objects.get(user=request.user, feed=article.feed).add()
		unread_count=UserArticleInfo.objects.filter(user=request.user, read=False).count()
		data=[{'feed':0, 'unread':unread_count}, {'feed':article.feed.pk, 'unread':feed_unread}]
	else:
		data=[]
	return JsonResponse(data, safe=False)


@login_required
def refresh_feed(request, feed):
	feed=int(feed)
	data=[]
	if feed!=0:
		feed=UserFeedSubscription.objects.get(pk=feed)
		feed.feed.update()
		data.append({'feed':feed.pk, 'unread':UserFeedCache.objects.get(user=request.user, feed=feed).unread})
	else:
		num_new_articles=0
		for user_feed in UserFeedSubscription.objects.filter(user=request.user, feed__last_updated__lt=datetime.now(timezone('utc')) - timedelta(minutes=10)):
			num_new_articles+=user_feed.feed.update()
			data.append({'feed':user_feed.pk, 'unread':UserFeedCache.objects.get(user=request.user, feed=user_feed).unread})
		logger.info('{} new article(s)'.format(num_new_articles))
	unread_count=UserArticleInfo.objects.filter(user=request.user, read=False).count()
	data.append({'feed':0, 'unread':unread_count})
	return JsonResponse(data, safe=False)


@login_required
def view_article(request, article):
	article=UserArticleInfo.objects.filter(user=request.user, article=article).select_related('article__content')
	return JsonResponse(article.values('article__content')[0], safe=False)


@login_required
def category_list(request):
	user_categories=Category.objects.filter(user=request.user).select_related('user__id')
	data=[]
	for category in user_categories:
		data.append(category.get_basic_info())
	return JsonResponse(data, safe=False)


@login_required
def view_feed_list(request):
	user_feeds=UserFeedSubscription.objects.filter(user=request.user).select_related('feed__id', 'feed__title', 'feed__success', 'feed__last_error', 'category__id')
	total_unread_count=UserFeedCache.objects.filter(user=request.user).aggregate(Sum('unread'))['unread__sum']
	individual_unread_count={}
	for feed in UserFeedCache.objects.filter(user=request.user).only('feed__id', 'unread'):
		individual_unread_count[feed.feed.feed_id]=feed.unread
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
	return JsonResponse(data, safe=False)


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

	articles=articles.select_related('article', 'feed__feed__id', 'feed__title', 'user__id')

	tmp=[]
	for user_article in articles[:limit]:
		tmp.append(user_article.get_basic_info())
	data['articles']=tmp
	data['unread']=max(data['unread'], 0)
	return JsonResponse(data, safe=False)


@login_required
def view_category_articles(request, category):
	category=int(category)
	data={}

	category=Category.objects.get(pk=category)
	articles=UserArticleInfo.objects.filter(user=request.user, feed__category=category)
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

	articles=articles.select_related('article', 'feed__feed__id', 'feed__title', 'user__id')

	tmp=[]
	for user_article in articles[:limit]:
		tmp.append(user_article.get_basic_info())
	data['articles']=tmp
	return JsonResponse(data, safe=False)


@require_POST
@login_required
def add_feed(request):
	form=AddFeedForm(request.POST)
	if form.is_valid():
		url=form.cleaned_data['url']
		try:
			user_feed=feed_utils.add_feed(request.user, url)
			data=user_feed.get_basic_info()
		except StandardError as e:
			data={'error':e.args}
	else:
		data={'error':'Input a valid url.'}
	return JsonResponse(data, safe=False)


@require_POST
@login_required
def edit_feed(request, feed):
	feed=int(feed)
	form=EditFeedForm(request.POST)
	user_feed=UserFeedSubscription.objects.get(user=request.user, pk=feed)
	feed=Feed.objects.get(pk=user_feed.feed.pk)
	changes=False
	if not form.is_valid():
		return JsonResponse({'form_errors':form.errors})
	if form.cleaned_data['feed_url']!=user_feed.feed.feed_url:
		url=form.cleaned_data['feed_url']
		check=feed_utils.check_feed(url, validity_check=False)
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
			valid=feed_utils.check_feed(url, existence_check=False)
			if valid[0] is not None:
				data={'error':'Error fetching feed.'}
			else:
				feed.feed_url=url
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
	data=user_feed.get_basic_info()
	return JsonResponse(data, safe=False)


@require_POST
@login_required
def delete_feed(request, feed):
	feed=int(feed)
	feed=UserFeedSubscription.objects.get(user=request.user, pk=feed)
	feed.delete()
	return JsonResponse({}, safe=False)
