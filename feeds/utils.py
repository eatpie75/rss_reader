# import os.path
import socket
from . import feedparser
from .models import Feed
# from urlparse import urljoin


def check_feed(url):
	if Feed.objects.filter(feed_url=url).exists():
		return (None, Feed.objects.get(feed_url=url).pk)
	old_timeout=socket.getdefaulttimeout()
	socket.setdefaulttimeout(25.0)
	feed=feedparser.parse(url)
	socket.setdefaulttimeout(old_timeout)
	if feed.bozo and not len(feed.entries):
		return (feed.bozo_exception, None)
	return (None, None)
