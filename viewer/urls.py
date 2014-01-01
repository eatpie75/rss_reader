from django.conf.urls import patterns, url

urlpatterns=patterns('',
	url(r'^$', 'viewer.views.index', name='index'),
)
