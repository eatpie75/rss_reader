import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from pytz import timezone
from time import mktime


class Feed(models.Model):
	feed_url=models.URLField()
	title=models.CharField(max_length=200, blank=True, null=True)
	site_url=models.URLField(blank=True, null=True)
	last_updated=models.DateTimeField(blank=True, null=True)
	update_interval=models.IntegerField(default=0)
	purge_interval=models.IntegerField(default=0)
	category=models.ForeignKey('Category', blank=True, null=True)

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
		if feed is None:
			feed=feedparser.parse(self.feed_url)
		if feed.status not in (404, 410, 500):
			print("Updating {}".format(self.title))
			for entry in feed.entries:
				if 'id' in entry:
					entry_id=entry.id
				else:
					entry_id=entry.link
				now=datetime.now(timezone('UTC'))
				if Article.objects.filter(feed=self, guid=entry_id).exists():
					Article.objects.filter(feed=self, guid=entry_id).update(date_last_seen=now)
					continue
				if 'published_parsed' in entry:
					date=datetime.fromtimestamp(mktime(entry.published_parsed))
					if 'updated_parsed' in entry:
						update_date=datetime.fromtimestamp(mktime(entry.updated_parsed))
					else:
						update_date=datetime.fromtimestamp(mktime(entry.published_parsed))
				elif 'updated_parsed' in entry:
					date=datetime.fromtimestamp(mktime(entry.updated_parsed))
					update_date=datetime.fromtimestamp(mktime(entry.updated_parsed))
				else:
					date=now
					update_date=now
				article=Article(
					feed=self,
					guid=entry_id,
					title=entry.title,
					url=entry.link,
					date_added=now,
					date_published=date,
					date_updated=update_date,
					date_last_seen=now
				)
				if 'content' in entry:
					article.content=unicode(BeautifulSoup(entry.content[0]['value']).body)[6:-7]
					article.description=unicode(BeautifulSoup(entry.description[:500]).body)[6:-7]
				elif 'description' in entry:
					article.content=unicode(BeautifulSoup(entry.description).body)[6:-7]
					article.description=unicode(BeautifulSoup(entry.description[:500]).body)[6:-7]
				else:
					article.content=entry.title
					article.description=entry.title[:500]
				article.save()
			self.last_updated=datetime.now(timezone('utc'))
			self.save()
		self.purge()

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
	guid=models.CharField(max_length=200)
	title=models.CharField(max_length=500)
	author=models.CharField(max_length=250, blank=True, null=True)
	date_added=models.DateTimeField()
	date_published=models.DateTimeField()
	date_updated=models.DateTimeField()
	date_last_seen=models.DateTimeField()
	description=models.TextField(blank=True, null=True)
	content=models.TextField(blank=True, null=True)
	url=models.URLField()
	read=models.BooleanField(default=False)

	@property
	def date_published_relative(self):
		now=datetime.now(timezone('UTC'))
		if now.day==self.date_published.day:
			return self.date_published.strftime('%I:%M %p')
		else:
			return self.date_published.strftime('%b %d, %Y')

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
