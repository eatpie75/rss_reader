import logging
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rssproject.settings")
import django
django.setup()

from apscheduler.schedulers.blocking import BlockingScheduler as Scheduler
from datetime import datetime
from django.conf import settings
from feeds.models import Feed
from pytz import timezone

try:
	from django.db import close_old_connections
except ImportError:
	from django.db import close_connection as close_old_connections

logging.config.dictConfig(settings.LOGGING)
logger=logging.getLogger('apscheduler.scheduler')


def update_feeds():
	feeds_updated=0
	i=0
	now=timezone('utc').localize(datetime.utcnow())
	for feed in Feed.objects.filter(next_fetch__lt=now).order_by('?'):
		i+=feed.update()
		feeds_updated+=1
		if feeds_updated>20:
			break
	if i>0:
		logger.info('{} new article(s)'.format(i))
	db.close_old_connections()
	return None


if __name__=='__main__':
	sched=Scheduler()
	sched.add_job(update_feeds, 'interval', minutes=1)
	sched.start()
