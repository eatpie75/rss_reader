import socket
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from feeds import feedparser
from pytz import timezone
from time import mktime


class Feed(models.Model):
	feed_url=models.URLField()
	title=models.CharField(max_length=200, blank=True, null=True)
	site_url=models.URLField(blank=True, null=True)
	last_fetched=models.DateTimeField(blank=True, null=True)
	last_updated=models.DateTimeField(blank=True, null=True)
	update_interval=models.IntegerField(default=0)
	purge_interval=models.IntegerField(default=0)
	category=models.ForeignKey('Category', blank=True, null=True)
	enabled=models.BooleanField(default=True)
	success=models.BooleanField(default=True)
	last_error=models.CharField(max_length=500, blank=True, null=True)

	@property
	def unread_count(self):
		return Article.objects.filter(feed=self, read=False).count()

	def initialize(self):
		feed=feedparser.parse(self.feed_url)
		print("Initializing {}".format(self.feed_url))
		if feed.status not in (404, 410, 500):
			self.title=feed.feed.title
			if 'link' in feed.feed:
				self.site_url=feed.feed.link
			self.last_updated=datetime.now(timezone('UTC'))
			self.save()
			self.update(feed)

	def update(self, feed=None):
		if not self.enabled:
			return 0
		old_timeout=socket.getdefaulttimeout()
		socket.setdefaulttimeout(25.0)
		i=0
		print("Updating {}:".format(self.title)),
		if feed is None:
			feed=feedparser.parse(self.feed_url)
		if (feed.bozo==0 or isinstance(feed.bozo_exception, feedparser.ThingsNobodyCaresAboutButMe)) and feed.status not in (404, 410, 500, 502):
			for entry in feed.entries:
				if 'id' in entry:
					entry_id=entry.id
				else:
					entry_id=entry.link
				now=datetime.utcnow()
				if Article.objects.filter(feed=self, guid=entry_id).exists():
					Article.objects.filter(feed=self, guid=entry_id).update(date_last_seen=timezone('utc').localize(now))
					continue
				i+=1
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
					feed=self,
					guid=entry_id,
					title=entry.title[:500],
					url=entry.link,
					date_added=timezone('utc').localize(now),
					date_published=timezone('utc').localize(date),
					date_updated=timezone('utc').localize(update_date),
					date_last_seen=timezone('utc').localize(now)
				)
				if 'content' in entry:
					article.content=unicode(BeautifulSoup(entry.content[0]['value'], 'html.parser'))
					article.description=unicode(BeautifulSoup(entry.description[:500], 'html.parser'))
				elif 'description' in entry:
					article.content=unicode(BeautifulSoup(entry.description, 'html.parser'))
					article.description=unicode(BeautifulSoup(entry.description[:500], 'html.parser'))
				else:
					article.content=entry.title
					article.description=entry.title[:500]
				article.save()
			print('Added {} new article(s)'.format(i))
			now=timezone('utc').localize(datetime.utcnow())
			self.last_fetched=now
			self.success=True
			if i>0:
				self.last_updated=now
			self.save()
		elif feed.bozo:
			print('exception')
			print(feed.bozo_exception)
			self.success=False
			self.last_error=str(feed.bozo_exception)
			self.save()
			# print(type(feed.bozo_exception))
			# print(isinstance(feed.bozo_exception, feedparser.ThingsNobodyCaresAboutButMe))
			if 'status' in feed: print(feed.status)
		# self.purge()
		socket.setdefaulttimeout(old_timeout)
		return i

	def purge(self):
		interval=self.purge_interval if self.purge_interval!=0 else settings.DEFAULT_ARTICLE_PURGE_INTERVAL
		interval=datetime.now(timezone('UTC'))-timedelta(days=interval)
		articles=Article.objects.filter(feed=self, date_added__lte=interval)
		for article in articles:
			if not article.read and not settings.PURGE_UNREAD:
				continue
			article.delete()

	def __unicode__(self):
		return unicode(self.title)

	class Meta:
		ordering=['title',]


class Article(models.Model):
	feed=models.ForeignKey(Feed)
	guid=models.CharField(db_index=True, max_length=200)
	title=models.CharField(max_length=500)
	author=models.CharField(max_length=250, blank=True, null=True)
	date_added=models.DateTimeField()
	date_published=models.DateTimeField()
	date_updated=models.DateTimeField()
	date_last_seen=models.DateTimeField()
	description=models.TextField(blank=True, null=True)
	content=models.TextField(blank=True, null=True)
	url=models.URLField()
	read=models.BooleanField(db_index=True, default=False)

	@property
	def date_published_relative(self):
		now=datetime.now(timezone('UTC'))
		if now.day==self.date_published.day:
			# return self.date_published.strftime('%I:%M %p')
			return self.date_published.astimezone(timezone('America/Los_Angeles')).strftime('%I:%M %p')
		else:
			# return self.date_published.strftime('%b %d, %Y')
			return self.date_published.astimezone(timezone('America/Los_Angeles')).strftime('%b %d, %Y')

	def __unicode__(self):
		return unicode(self.title)

	class Meta:
		ordering=['-date_published', '-date_added', '-id']


class Category(models.Model):
	name=models.CharField(max_length=50)
	parent=models.ForeignKey('Category', blank=True, null=True)

	def __unicode__(self):
		return unicode(self.name)

	class Meta:
		ordering=['name',]
		verbose_name_plural='categories'


@receiver(post_save, sender=Feed, dispatch_uid='feeds.add_feed')
def add_feed(sender, **kwargs):
	if kwargs['created']:
		kwargs['instance'].initialize()


def fix_timestamp_dst(tt):
	tt=list(tt)
	tt[-1]=-1
	return tt
