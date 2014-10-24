import logging
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rssproject.settings")
import django
django.setup()

from apscheduler.schedulers.blocking import BlockingScheduler as Scheduler
from datetime import datetime
from django import db
from django.conf import settings
from feeds.models import Feed
from pytz import timezone


logging.config.dictConfig(settings.LOGGING)
logger=logging.getLogger('apscheduler.scheduler')


def update_feeds():
	f=0
	i=0
	now=timezone('utc').localize(datetime.utcnow())
	for feed in Feed.objects.filter(next_fetch__lt=now).order_by('?'):
		i+=feed.update()
		f+=1
		if f>20:
			break
	if i>0:
		logger.info('{} new article(s)'.format(i))
	db.close_connection()
	return None


if __name__=='__main__':
	sched=Scheduler()
	sched.add_job(update_feeds, 'interval', minutes=1)
	sched.start()
