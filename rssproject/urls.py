from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns=patterns('',
	# Examples:
	url(r'^feeds/', include('feeds.urls')),
	url(r'^$', include('viewer.urls')),
	url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':'login.html.j2'}),
	# url(r'^rss/', include('rss.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
)
