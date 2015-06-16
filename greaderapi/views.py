from datetime import datetime
# from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from dejango.template.defaultfilters import striptags
from django.views.decorators.http import require_POST, require_GET
from feeds.models import UserFeedSubscription, UserArticleInfo, UserFeedCache, Category
from feeds.utils import add_feed
from .models import Token
import re


def get_user(request):
	token=request.META['HTTP_AUTHORIZATION']
	if not token.startswith('GoogleLogin auth='):
		raise StandardError('No auth token')
		# return HttpResponse(status_code=401)
	token=token[17:]
	test=Token.objects.filter(token=token)
	if not test.exists():
		raise StandardError('Auth token not found')
		# return HttpResponse(status_code=401)
	if token.expires>datetime.now():
		raise StandardError('Auth token expired')
	user=test[0].user
	return user


def clean_id(full_id):
	label_re=re.compile(r'user\/(?:-|\d*?)\/label\/(.*?)')
	state_re=re.compile(r'user\/(?:-|\d*?)\/state\/com\.google\/(?:un)?read')

	if full_id.startswith('feed/'):
		return ('feed', full_id[5:])
	elif label_re.match(full_id):
		return ('category', clean_category(full_id))
	elif state_re.match(full_id):
		if full_id.endswith('unread'):
			return ('state', 'unread')
		else:
			return ('state', 'read')


def get_qs_from_id(full_id, **kwargs):
	stream=clean_id(full_id)
	user=kwargs.get('user', None)
	if stream[0]=='feed':
		if user is None:
			raise StandardError('Passed a feed without user')
		feed=stream[1]
		feed_qs=UserFeedSubscription.objects.filter(user=user, feed___feed_url=feed)
		if not feed_qs.exists():
			raise StandardError('Feed not found')
		feed=feed_qs[0]
		return feed
	elif stream[0]=='category':
		if user is None:
			raise StandardError('Passed a category without user')
		category=stream[1]
		return get_category(user, category)
	# elif stream[0]=='state':
	# 	if stream[1]=='unread':
	# 		read=False
	# 	else:
	# 		read=True


def clean_article(full_id):
	if not full_id.startswith('tag:google.com,2005:reader/item/'):
		raise StandardError('Invalid item id')
	article=full_id[32:]
	return article


def get_article(user, article):
	article=UserArticleInfo.objects.filter(user=user, article_id=article)
	if article.exists():
		return article[0]
	else:
		raise StandardError('Article not found')


def clean_category(full_id):
	category=striptags(full_id)
	if '/label/' in category:
		category=category.split('/label/', 1)[1]
		category.strip()
		category.replace('/', '')
		return category
	else:
		raise StandardError('Invalid category id')


def get_category(user, category):
	category=Category.objects.filter(user=user, name=category)
	if category.exists():
		return category[0]
	else:
		raise StandardError('Category not found')


@require_GET()
def user_info(request):
	try:
		user=get_user(request)
	except StandardError:
		return HttpResponse(status_code=401)
	return JsonResponse({
		'userId':user.pk,
		# 'userId':'-',
		'userProfileId':user.pk,
		'userName':user.username,
		'userEmail':user.email,
		'SignupTimeSec':0,
		'isBloggerUser':True,
		'isMultiLoginEnabled':False
	})


@require_GET()
def unread_count(request):
	try:
		user=get_user(request)
	except StandardError:
		return HttpResponse(status_code=401)
	unread_counts=[]
	total_unread_count=UserFeedCache.objects.filter(user=user).aggregate(Sum('unread'))['unread__sum']
	if total_unread_count>0:
		unread_counts.append({
			'id':'user/-/state/com.google/reading-list', 'count':total_unread_count, 'newestItemTimestampUsec':0
		})
	for feed_cache in UserFeedCache.objects.filter(user=user).only('feed__id', 'unread', 'feed__feed__feed_url'):
		unread_counts.append({
			'id':'feed/{}'.format(feed_cache.feed.feed.feed_url),
			'count':feed_cache.unread,
			'newestItemTimestampUsec':0,
		})
	# data={'total_unread_count':max(total_unread_count, 0)}
	data={'max':1000, 'unreadcounts':unread_counts}
	return JsonResponse(data, safe=False)


@require_GET()
def subscription_list(request):
	try:
		user=get_user(request)
	except StandardError:
		return HttpResponse(status_code=401)
	user_feeds=UserFeedSubscription.objects.filter(user=user)
	subscriptions=[]
	for user_feed in user_feeds:
		iconUrl=user_feed.feed.get_feed_image()
		if iconUrl is None:
			iconUrl=''
		subscription={
			'id':'feed/{}'.format(user_feed.feed.feed_url),
			'title':user_feed.title,
			'firstitemmsec':0,
			'url':user_feed.feed.feed_url,
			'htmlUrl':user_feed.feed.site_url,
			'iconUrl':iconUrl,
			'categories':[],
		}
		if user_feed.category is not None:
			subscription.categories.append({
				'id':'user/{}/label/{}'.format(user.pk, user_feed.category.pk),
				'label':user_feed.category.name,
			})
		subscriptions.append(subscription)
	data={'subscriptions':subscriptions}
	return JsonResponse(data, safe=False)


@require_POST()
def subscription_edit(request):
	try:
		user=get_user(request)
	except StandardError:
		return HttpResponse(status_code=401)
	if 'ac' not in request.POST or 's' not in request.POST:
		return HttpResponse(status_code=401)
	if request.POST['ac'] not in ('edit', 'subscribe', 'unsubscribe'):
		return HttpResponse(status_code=401)
	action=request.POST['ac']
	if not request.POST['s'].startswith('feed/'):
		return HttpResponse(status_code=401)
	feed=request.POST['s'][5:]
	if action=='edit':
		feed_qs=UserFeedSubscription.objects.filter(user=user, feed___feed_url=feed)
		if not feed_qs.exists():
			return HttpResponse(status_code=401)
		feed=feed_qs[0]
		feed_changed=False
		if 't' in request.POST:
			title=striptags(request.POST['t'])
			feed.title=title
			feed_changed=True
		if 'a' in request.POST:
			new_category=clean_category(request.POST['a'])
			new_category_qs=Category.objects.filter(user=user, name=new_category)
			if new_category_qs.exists():
				new_category=Category.objects.get(user=user, name=new_category)
				if feed.category!=new_category:
					feed.category=new_category
					feed_changed=True
			else:
				new_category=Category(user=user, name=new_category)
				new_category.save()
				feed.category=new_category
				feed_changed=True
		elif 'r' in request.POST:
			new_category=striptags(request.POST['a'])
			if '/label/' in new_category:
				feed.category=None
				feed_changed=True
		if feed_changed:
			feed.save()
		return HttpResponse('OK', status_code=200)
	elif action=='subscribe':
		if UserFeedSubscription.objects.filter(user=user, feed_id=feed).exists():
			return HttpResponse('OK', status_code=200)
		else:
			add_feed(user, feed)
			return HttpResponse('OK', status_code=200)
	elif action=='unsubscribe':
		feed_qs=UserFeedSubscription.objects.filter(user=user, feed___feed_url=feed)
		if feed_qs.exists():
			feed=feed_qs[0]
			feed.delete()
		return HttpResponse('OK', status_code=200)


@require_POST()
def subscription_quickadd(request):
	try:
		user=get_user(request)
	except StandardError:
		return HttpResponse(status_code=401)
	if not request.POST['quickadd'].startswith('feed/'):
		return HttpResponse(status_code=401)
	feed=request.POST['quickadd'][5:]
	if UserFeedSubscription.objects.filter(user=user, feed_id=feed).exists():
		feed=UserFeedSubscription.objects.get(user=user, feed_id=feed)
	else:
		feed=add_feed(user, feed)
	data={
		'query':'feed/{}'.format(feed.feed.feed_url),
		'numResults':1,
		'streamId':'feed/{}'.format(feed.feed.feed_url),
		'streamName':feed.title
	}
	return JsonResponse(data, safe=False)


@require_GET()
def tag_list(request):
	try:
		user=get_user(request)
	except StandardError:
		return HttpResponse(status_code=401)
	data=[]
	for category in Category.objects.filter(user=user):
		data.append({
			'id':'user/{}/label/{}'.format(user.pk, category.name),
			'sortId':'FFFFFFFF',
		})
	return JsonResponse(data, safe=False)


@require_POST()
def tag_rename(request):
	try:
		user=get_user(request)
	except StandardError:
		return HttpResponse(status_code=401)
	if 's' not in request.POST or 'dest' not in request.POST:
		return HttpResponse(status_code=401)
	old_category_name=clean_category(request.POST['s'])
	new_category_name=clean_category(request.POST['s'])
	if old_category_name==new_category_name:
		return HttpResponse('OK', status_code=200)
	try:
		category=get_category(user, old_category_name)
		category.name=new_category_name
		category.save()
		return HttpResponse('OK', status_code=200)
	except StandardError:
		return HttpResponse(status_code=401)


@require_POST()
def tag_delete(request):
	try:
		user=get_user(request)
	except StandardError:
		return HttpResponse(status_code=401)
	if 's' not in request.POST:
		return HttpResponse(status_code=401)
	category_name=clean_category(request.POST['s'])
	try:
		category=get_category(user, category_name)
		category.delete()
	except StandardError:
		return HttpResponse(status_code=401)


@require_POST()
def tag_edit(request):
	try:
		user=get_user(request)
	except StandardError:
		return HttpResponse(status_code=401)
	if 'a' not in request.POST and 'r' not in request.POST:
		return HttpResponse(status_code=401)
	if len(request.POST['a'])>10 or len(request.POST['a'])>10:
		return HttpResponse(status_code=401)
	if 'i' not in request.POST:
		return HttpResponse(status_code=401)
	if request.POST['a']==request.POST['r']:
		return HttpResponse(status_code=401)
	add_set=set(request.POST['a'])
	rem_set=(request.POST['r'])
	add_list=list(add_set - rem_set)
	rem_list=list(rem_set - add_set)
	for addition in add_list:
		if addition.endswith('/state/com.google/read'):
			for article in request.POST['i']:
				article=clean_article(article)
				article=get_article(user, article)
				if not article.read:
					article.change_read_state(True)
	for removal in rem_list:
		if removal.endswith('/state/com.google/read'):
			for article in request.POST['i']:
				article=clean_article(article)
				article=get_article(user, article)
				if not article.read:
					article.change_read_state(False)
	return HttpResponse('OK', status_code=200)


@require_GET()
def stream_contents(request, stream_id):
	def add_filter(qs, stream_id, user=None, exclude=False):
		stream=clean_id(stream_id)
		if not exclude:
			func=qs.filter
		else:
			func=qs.exclude
		if stream[0]=='feed':
			qs=func(feed=get_qs_from_id(stream_id, user=user))
		elif stream[0]=='category':
			qs=func(feed__category=get_qs_from_id(stream_id, user=user))
		elif stream[0]=='state':
			if stream[1]=='unread':
				read=False
			else:
				read=True
			qs=func(read=read)
		return qs

	try:
		user=get_user(request)
	except StandardError:
		return HttpResponse(status_code=401)

	items=UserArticleInfo.objects.filter(user=user)

	items=add_filter(items, stream_id, user)

	limit=50
	if 'n' in request.GET:
		limit=min(int(request.GET['n']), 1000)

	reverse_order=False
	if 'r' in request.GET:
		if request.GET['r']=='o':
			reverse_order=True
			items=items.order_by('article__date_published', 'article__date_added', 'article__id')

	if 'ot' in request.GET:
		last_article=datetime.utcfromtimestamp(request.GET['ot'])
		items=items.filter(article__date_published__lt=last_article)

	if 'xt' in request.GET:
		for exclude in request.GET['xt']:
			items=add_filter(items, exclude, user, True)

	if 'it' in request.GET:
		for exclude in request.GET['it']:
			items=add_filter(items, exclude, user)

	if 'c' in request.GET:
		pass

	data={
		'direction':'ltr',
		'id':'',
		'title':'',
		'description':'',
		'self':{
			'href':'',
		},
		'updated':0,
		'updatedUsec':0,
		'items':[],
		'continuation':'',
	}
	for user_article in items[:limit]:
		tmp={
			'crawlTimeMsec':0,
			'timestampUsec':0,
			'id':'',
			'categories':[
				'user/{}/state/com.google/reading-list'.format(user.pk),
			],
			'title':user_article.article.title,
			'published':user_article.article.date_published,
			'updated':user_article.article.date_updated,
			'canonical':[{
				'href':user_article.article.url,
			}],
			'alternate':[{
				'href':user_article.article.url,
				'type':'text/html',
			}],
			'summary':{
				'direction':'ltr',
				'content':user_article.article.content,
			},
			'author':user_article.article.author,
			'likingUsers':[],
			'comments':[],
			'commentsNum':-1,
			'annotations':[],
			'origin':{
				'streamId':'',
				'title':user_article.feed.title,
				'htmlUrl':user_article.feed.feed.site_url
			}
		}
		if user_article.read:
			tmp['categories'].append('user/{}/state/com.google/read'.format(user.pk))
		if user_article.feed.get_category() is not None:
			tmp['categories'].append('user/{}/label/{}'.format(user.pk, user_article.feed.category))
		data['items'].append(tmp)

	return JsonResponse(data, safe=False)
