import logging
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rssproject.settings")

from apscheduler.scheduler import Scheduler
from datetime import datetime
from django import db
from feeds.models import Feed
from pytz import timezone


logging.getLogger('apscheduler.scheduler').addHandler(logging.StreamHandler())


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
		print('{} new article(s)'.format(i))
	db.close_connection()
	return None


if __name__=='__main__':
	sched=Scheduler(standalone=True)
	sched.add_interval_job(update_feeds, minutes=1)
	sched.start()
