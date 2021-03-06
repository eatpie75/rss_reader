import requests
import socket
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models
from django.db.models import F, Sum
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from feeds import feedparser
from io import BytesIO
from jsonfield import JSONField
from PIL import Image
from pytz import timezone
from time import mktime
from urlparse import urljoin

import logging
logger=logging.getLogger(__name__)


class Feed(models.Model):
	id=models.AutoField(primary_key=True, db_index=True)
	title=models.TextField(blank=True)
	feed_url=models.URLField(max_length=500)
	site_url=models.URLField(max_length=500, blank=True, null=True)
	feed_image=models.ImageField(upload_to='feeds', blank=True, null=True)
	date_added=models.DateTimeField(blank=True, null=True)
	last_fetched=models.DateTimeField(blank=True, null=True)
	last_updated=models.DateTimeField(blank=True, null=True)
	update_interval=models.IntegerField(default=300, help_text='Base time between updates in minutes')
	next_fetch=models.DateTimeField(blank=True, null=True)
	purge_interval=models.IntegerField(default=0)
	enabled=models.BooleanField(default=True)
	success=models.BooleanField(default=True)
	last_error=models.CharField(max_length=500, blank=True)
	statistics=JSONField(default={})
	statistics_updated=models.DateTimeField(blank=True, null=True)

	def initialize(self):
		tmp=self.get_feed()
		if tmp[0] is None:
			feed=tmp[1]
		else:
			self.success=False
			self.enabled=False
			self.save()
			return False

		logging.info("Initializing {}".format(self.feed_url))
		self.title=feed.feed.title[:500]
		if 'link' in feed.feed:
			self.site_url=feed.feed.link
		now=timezone('utc').localize(datetime.utcnow())
		self.date_added=now
		self.last_updated=now
		self.save()
		self.update_statistics()
		self.update(feed)
		self.get_favicon(feed)
		self.update_statistics()

	def get_feed(self):
		old_timeout=socket.getdefaulttimeout()
		socket.setdefaulttimeout(25.0)
		feed=feedparser.parse(self.feed_url)
		socket.setdefaulttimeout(old_timeout)
		if feed.bozo and not len(feed.entries):
			logger.error('exception')
			logger.error(feed.bozo_exception)
			if 'status' in feed:
				logger.info('feed status :{}'.format(feed.status))
			self.success=False
			self.last_error=str(feed.bozo_exception)
			self.save()
			return (feed.bozo_exception, None)
		if feed.status==301:
			logger.info('got status:301, updating feed url to:{}'.format(feed.href))
			self.feed_url=feed.href
		elif not 199<feed.status<300:
			logger.error('got status:{}'.format(feed.status))
		return (None, feed)

	def get_favicon(self, feed=None):
		if feed is None:
			tmp=self.get_feed()
			if tmp[0] is None:
				feed=tmp[1]
			else:
				return None

		if 'icon' in feed.feed:
			url=feed.feed.icon
			logger.info('got icon from rss: {}'.format(url))
		else:
			tmp=requests.get(self.site_url)
			if 400<=tmp.status_code<=510:
				logger.error('site status code: {}'.format(tmp.status_code))
				return None
			tmp=BeautifulSoup(tmp.text)
			tmp=tmp.find('link', rel='icon')
			if tmp is not None:
				url=urljoin(self.site_url, tmp['href'])
				logger.info('got icon from html: {}'.format(url))
			else:
				url=urljoin(self.site_url, '/favicon.ico')
				logger.info('attempting to get icon from favicon.ico: {}'.format(url))
		icon=requests.get(url)
		if 400<=icon.status_code<=510:
			logger.error('got status: {} on {}'.format(icon.status_code, url))
			return None
		icon=File(BytesIO(icon.content))
		output=File(BytesIO())
		try:
			image=Image.open(icon)
			logger.debug('really opened image')
		except:
			return None
		if image.mode!='RGBA':
			image=image.convert('RGBA')
		if image.size!=(16, 16):
			image=image.resize((16, 16), Image.ANTIALIAS)
		image.save(output, 'PNG', optimize=True)
		if self.feed_image is not None:
			self.feed_image.delete()
		self.feed_image.save('{}.png'.format(self.pk), output)
		return True

	def update(self, feed=None):
		if not self.enabled:
			return 0

		i=0
		logger.info("Updating {}".format(self.title))

		if feed is None:
			tmp=self.get_feed()
			if tmp[0] is None:
				feed=tmp[1]
			else:
				self.next_fetch=timezone('utc').localize(datetime.utcnow()) + timedelta(minutes=self.get_next_fetch())
				self.save()
				return i

		for entry in feed.entries:
			new_article=add_article(self, entry)
			if new_article:
				i+=1
		logger.info('Added {} new article(s)'.format(i))
		now=timezone('utc').localize(datetime.utcnow())
		self.last_fetched=now
		self.next_fetch=now + timedelta(minutes=self.get_next_fetch())
		self.success=True
		if i>0:
			self.last_updated=now
			recalulate_feed_cache(self.pk)
		self.save()

		if self.needs_statistics_update:
			self.update_statistics()
		# self.purge()
		return i

	def update_statistics(self):
		logger.info('Updating statistics for {}'.format(self.title))
		data={}
		i=0
		for article in Article.objects.filter(feed=self).only('date_published'):
			date=article.date_published
			weekday=date.weekday()
			hour=date.hour
			if weekday not in data:
				data[weekday]={'count':0}
			if hour not in data[weekday]:
				data[weekday][hour]=0
			data[weekday]['count']+=1
			data[weekday][hour]+=1
			i+=1
		data['total']=i
		self.statistics=data
		self.statistics_updated=timezone('utc').localize(datetime.utcnow())
		self.save()
		logger.info('Updated statistics for {}'.format(self.title))

	def get_next_fetch(self):
		now=timezone('utc').localize(datetime.utcnow())
		data=self.statistics
		if now.hour==23 and now.minute>=30:
			now+=timedelta(minutes=30)
		day=data.get(now.weekday(), {}).get('count', 0)
		hour=data.get(now.weekday(), {}).get(now.hour, 0)

		mod=1.0
		long_interval=False
		if self.last_updated<now - timedelta(days=180):
			mod*=3
		elif self.last_updated<now - timedelta(days=60):
			mod*=2
		elif self.last_updated<now - timedelta(days=30):
			mod*=1.5
		elif self.last_updated<now - timedelta(days=7):
			mod*=1.05
		if self.last_updated<now - timedelta(days=30):
			long_interval=True

		if not long_interval:
			if day>=data['total'] / 7.0 / 1:
				mod*=0.75
			elif day<=data['total'] / 7.0 / 1 / 2:
				mod*=1.25

			if hour>=data['total'] / 24.0 / 2:
				mod*=0.8
			elif hour<=data['total'] / 24.0 / 2 / 2:
				mod*=1.2

		if not self.success:
			mod*=1.5

		return int(round(self.update_interval * mod))

	# def purge(self):
	# 	interval=self.purge_interval if self.purge_interval!=0 else settings.DEFAULT_ARTICLE_PURGE_INTERVAL
	# 	interval=datetime.now(timezone('UTC')) - timedelta(days=interval)
	# 	articles=Article.objects.filter(feed=self, date_added__lte=interval)
	# 	for article in articles:
	# 		if not article.read and not settings.PURGE_UNREAD:
	# 			continue
	# 		article.delete()

	def get_basic_info(self):
		return {
			'pk':self.pk,
			'enabled':self.enabled,
			'success':self.success,
			'title':self.title,
			'site_url':self.site_url,
			'image':self.get_feed_image
		}

	def get_all_info(self):
		return {
			'pk':self.pk,
			'enabled':self.enabled,
			'success':self.success,
			'title':self.title,
			'feed_url':self.feed_url,
			'site_url':self.site_url,
			'image':self.get_feed_image,
			'last_fetched':self.last_fetched,
			'last_updated':self.last_updated,
			'update_interval':self.update_interval,
			'next_fetch':self.next_fetch,
			'needs_update':self.needs_update
		}

	@property
	def get_feed_image(self):
		if self.feed_image is not None and self.feed_image!='':
			return self.feed_image.url
		else:
			return None

	@property
	def needs_update(self):
		return self.next_fetch<timezone('utc').localize(datetime.utcnow())

	@property
	def needs_statistics_update(self):
		return self.statistics_updated + timedelta(days=7)<timezone('utc').localize(datetime.utcnow())

	def __unicode__(self):
		return unicode(self.title)

	class Meta:
		ordering=['title',]


class Article(models.Model):
	id=models.AutoField(primary_key=True, db_index=True)
	feed=models.ForeignKey(Feed)
	guid=models.TextField(db_index=True)
	title=models.TextField()
	author=models.CharField(max_length=250, blank=True)
	date_added=models.DateTimeField()
	date_published=models.DateTimeField()
	date_updated=models.DateTimeField()
	date_last_seen=models.DateTimeField()
	description=models.TextField(blank=True)
	content=models.TextField(blank=True)
	url=models.URLField(max_length=500)

	def create_user_info(self):
		tmp=[]
		for subscription in UserFeedSubscription.objects.filter(feed=self.feed).only('user'):
			tmp.append(UserArticleInfo(user=subscription.user, feed=subscription, article=self))
		UserArticleInfo.objects.bulk_create(tmp)
		del tmp
		return True

	@property
	def date_published_relative(self):
		now=datetime.now(timezone('UTC'))
		if now.date()==self.date_published.date():
			return self.date_published.astimezone(timezone('America/Los_Angeles')).strftime('%I:%M %p')
		else:
			return self.date_published.astimezone(timezone('America/Los_Angeles')).strftime('%b %d, %Y')

	def __unicode__(self):
		return unicode(self.title)

	class Meta:
		ordering=['-date_published', '-date_added', '-id']


class UserFeedSubscription(models.Model):
	user=models.ForeignKey(User, db_index=True)
	feed=models.ForeignKey(Feed, db_index=True)
	title=models.TextField(blank=True)
	date_added=models.DateTimeField(auto_now_add=True)
	category=models.ForeignKey('Category', blank=True, null=True)

	@property
	def unread(self):
		return UserFeedCache.objects.get(user=self.user, feed=self.feed).unread

	@property
	def get_category(self):
		return self.category.pk if self.category is not None else None

	def get_basic_info(self):
		tmp=self.feed.get_basic_info()
		tmp.update({'pk':self.pk, 'title':self.title, 'category':self.get_category})
		return tmp

	def get_all_info(self):
		tmp=self.feed.get_all_info()
		tmp.update({'pk':self.pk, 'title':self.title, 'category':self.get_category})
		return tmp

	def __unicode__(self):
		return unicode(self.title)

	class Meta:
		ordering=['title',]
		unique_together=[['user', 'feed'],]


class UserArticleInfo(models.Model):
	user=models.ForeignKey(User, db_index=True)
	feed=models.ForeignKey(UserFeedSubscription, db_index=True)
	article=models.ForeignKey(Article, db_index=True)
	read=models.BooleanField(db_index=True, default=False)
	date_read=models.DateTimeField(blank=True, null=True)

	def change_read_state(self, state=None):
		if state is None:
			state=not self.read
		if self.read==state:
			return UserFeedCache.objects.get(user=self.user, feed=self.feed).unread
		self.read=state
		if self.read:
			self.date_read=timezone('utc').localize(datetime.utcnow())
		else:
			self.date_read=None
		self.save()
		if self.read:
			return UserFeedCache.objects.get(user=self.user, feed=self.feed).sub()
		else:
			return UserFeedCache.objects.get(user=self.user, feed=self.feed).add()

	def get_basic_info(self):
		return {
			'pk':self.pk,
			'user':self.user.pk,
			'feed':{
				'pk':self.feed.pk,
				'title':self.feed.title,
				'image':self.feed.feed.get_feed_image if self.feed.feed.get_feed_image is not None else settings.STATIC_URL + 'img/rss.png'
			},
			'article':{
				'pk':self.article.pk,
				'title':self.article.title,
				'author':self.article.author,
				'date_published':self.article.date_published,
				'date_published_relative':self.article.date_published_relative,
				'date_added':self.article.date_added,
				# 'description':self.article.description,
				# 'content':self.article.content,
				'url':self.article.url
			},
			'read':self.read,
			'date_read':self.date_read
		}

	class Meta:
		index_together=[['user', 'feed'], ['user', 'feed', 'read']]
		ordering=['-article__date_published', '-article__date_added', '-article__id']
		unique_together=[['user', 'feed', 'article']]


class UserFeedCache(models.Model):
	user=models.ForeignKey(User)
	feed=models.ForeignKey(UserFeedSubscription)
	unread=models.PositiveIntegerField(default=0)

	def recalculate(self):
		self.unread=UserArticleInfo.objects.filter(user=self.user, feed=self.feed, read=False).count()
		self.save()
		return self

	def add(self, value=1):
		self.unread=F('unread') + value
		self.save()
		return UserFeedCache.objects.get(id=self.id).unread

	def sub(self, value=1):
		self.unread=F('unread') - value
		self.save()
		return UserFeedCache.objects.get(id=self.id).unread

	class Meta:
		index_together=[['user', 'feed'],]
		unique_together=[['user', 'feed'],]


class Category(models.Model):
	user=models.ForeignKey(User)
	name=models.CharField(max_length=50)
	parent=models.ForeignKey('Category', blank=True, null=True)
	expanded=models.BooleanField(default=True)

	def change_expanded_state(self, state=None):
		if state is None:
			state=not self.expanded
		if self.expanded==state:
			return self.expanded
		self.expanded=state
		self.save()
		return self.expanded

	def get_basic_info(self):
		return {
			'pk':self.pk,
			'user':self.user.pk,
			'name':self.name,
			'parent':self.parent,
			'expanded':self.expanded,
		}

	def __unicode__(self):
		return unicode(self.name)

	class Meta:
		ordering=['name',]
		verbose_name_plural='categories'


def recalculate_user_cache(user):
	user=User.objects.get(pk=user)
	for cache in UserFeedCache.objects.filter(user=user):
		cache.recalculate()
	return UserFeedCache.objects.filter(user=user).aggregate(Sum('unread'))['unread__sum']


def recalulate_feed_cache(feed):
	feed=Feed.objects.get(pk=feed)
	for cache in UserFeedCache.objects.filter(feed__feed=feed):
		cache.recalculate()
	return True


@receiver(post_save, sender=Feed, dispatch_uid='feeds.add_feed')
def add_feed(sender, **kwargs):
	if kwargs['created']:
		kwargs['instance'].initialize()


@receiver(pre_delete, sender=Feed, dispatch_uid='feeds.delete_feed')
def delete_feed(sender, **kwargs):
	instance=kwargs['instance']
	if instance.feed_image is not None:
			instance.feed_image.delete()


@receiver(pre_delete, sender=UserFeedSubscription, dispatch_uid='feeds.delete_subscription')
def delete_subscription(sender, **kwargs):
	instance=kwargs['instance']
	UserArticleInfo.objects.filter(user=instance.user, feed__feed=instance.feed).delete()
	UserFeedCache.objects.filter(user=instance.user, feed__feed=instance.feed).delete()
	if UserFeedSubscription.objects.filter(feed=instance.feed).count() - 1==0:
		Feed.objects.filter(pk=instance.feed_id).update(enabled=False)


def add_article(feed, entry):
	if 'id' in entry:
		entry_id=entry.id
	else:
		entry_id=entry.link
	now=datetime.utcnow()
	if Article.objects.filter(feed=feed, guid=entry_id).exists():
		Article.objects.filter(feed=feed, guid=entry_id).update(date_last_seen=timezone('utc').localize(now))
		return False
	if 'published_parsed' in entry and entry.published_parsed is not None:
		date=datetime.fromtimestamp(mktime(fix_timestamp_dst(entry.published_parsed)))
		if 'updated_parsed' in entry:
			update_date=datetime.fromtimestamp(mktime(fix_timestamp_dst(entry.updated_parsed)))
		else:
			update_date=date
	elif 'updated_parsed' in entry:
		date=datetime.fromtimestamp(mktime(fix_timestamp_dst(entry.updated_parsed)))
		update_date=date
	else:
		date=now
		update_date=now
	article=Article(
		feed=feed,
		guid=entry_id,
		title=unicode(entry.title[:500]),
		url=entry.link,
		date_added=timezone('utc').localize(now),
		date_published=timezone('utc').localize(date),
		date_updated=timezone('utc').localize(update_date),
		date_last_seen=timezone('utc').localize(now)
	)
	if 'content' in entry:
		content=unicode(entry.content[0]['value'])
		description=unicode(entry.description[:500])
	elif 'description' in entry:
		content=unicode(entry.description)
		description=unicode(entry.description[:500])
	else:
		content=unicode(entry.title)
		description=unicode(entry.title[:500])
	if 'author' in entry:
		article.author=entry.author
	content=BeautifulSoup(content, 'html.parser')
	description=BeautifulSoup(description, 'html.parser')
	for tracking_img in content.find_all('img', height=1, width=1):
		tracking_img.decompose()
	article.content=unicode(content)
	article.description=unicode(description)
	article.save()
	article.create_user_info()
	return True


def fix_timestamp_dst(tt):
	tt=list(tt)
	tt[-1]=-1
	return tt
