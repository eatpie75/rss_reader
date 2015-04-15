# import os.path
import socket
from . import feedparser
from .models import Feed, Article, UserFeedSubscription, UserFeedCache, UserArticleInfo
# from urlparse import urljoin

import logging
logger=logging.getLogger(__name__)


def check_feed(url, **kwargs):
	existence_check=kwargs.get('existence_check', True)
	validity_check=kwargs.get('validity_check', True)
	if existence_check and feed_exists(url):
		return (None, Feed.objects.get(feed_url=url).pk)
	if validity_check:
		feed=get_feed(url)
		if feed_parseable(feed):
			return (None, None)
		else:
			return (feed.bozo_exception, None)
	return (None, None)


def feed_exists(url):
	return Feed.objects.filter(feed_url=url).exists()


def get_feed(url):
	old_timeout=socket.getdefaulttimeout()
	socket.setdefaulttimeout(25.0)
	feed=feedparser.parse(url)
	socket.setdefaulttimeout(old_timeout)
	return feed


def feed_parseable(feed):
	if feed.bozo and not len(feed.entries):
		return False
	else:
		return True


def add_feed(user, url, title=None):
	feed=check_feed(url)
	if feed[0] is not None:
		raise StandardError('Error fetching feed')
	else:
		if type(feed[1])!=int:
			feed=Feed(feed_url=url)
			feed.save()
			logger.info('Created new feed: {}'.format(feed.feed_url))
		elif type(feed[1])==int:
			feed=Feed.objects.get(pk=feed[1])
			if feed.enabled is False:
				feed.enabled=True
			if feed.needs_update:
				feed.update()
		if title is None:
			title=feed.title
		user_feed=UserFeedSubscription(user=user, feed=feed, title=title)
		user_feed.save()
		tmp=[]
		for article in Article.objects.filter(feed=feed.pk).only('pk')[:25]:
			tmp.append(UserArticleInfo(user=user, feed=user_feed, article=article))
		UserArticleInfo.objects.bulk_create(tmp)
		del tmp
		UserFeedCache(user=user, feed=user_feed).recalculate()
		return user_feed
