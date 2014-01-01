# import os.path
import socket
from . import feedparser
from .models import Feed
# from urlparse import urljoin


def check_feed(url, existence_check=True):
	if existence_check and feed_exists(url):
		return (None, Feed.objects.get(feed_url=url).pk)
	feed=get_feed(url)
	if feed_parseable(feed):
		return (None, None)
	else:
		return (feed.bozo_exception, None)


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
