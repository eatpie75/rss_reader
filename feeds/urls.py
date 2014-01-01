from django.conf.urls import patterns, url

urlpatterns=patterns('feeds.views',
	# url(r'^(?P<feed>\d{1,12})/unread$', 'feed_unread', name='feed_unread'),
	url(r'^feeds/add/$', 'add_feed', name='add_feed'),
	url(r'^feeds/list/$', 'view_feed_list', name='view_feed_list'),
	url(r'^feeds/(?P<feed>\d{1,12})/info$', 'feed_info', name='feed_info'),
	url(r'^feeds/(?P<feed>\d{1,12})/edit$', 'edit_feed', name='edit_feed'),
	url(r'^feeds/(?P<feed>\d{1,12})/refresh$', 'refresh_feed', name='refresh_feed'),
	url(r'^feeds/(?P<feed>\d{1,12})/mark_read$', 'mark_all_read', name='mark_all_read'),
	url(r'^feeds/(?P<feed>\d{1,12})/articles$', 'view_feed_articles', name='view_feed_articles'),
	# url(r'^(?P<feed>\d{1,12})/$', 'view_feed_info', name='view_feed_info'),
	url(r'^article/(?P<article>\d{1,12})/read$', 'mark_read', name='mark_read'),
	url(r'^article/(?P<article>\d{1,12})/unread$', 'mark_unread', name='mark_unread'),
	url(r'^article/(?P<article>\d{1,12})/$', 'view_article', name='view_article'),
)
