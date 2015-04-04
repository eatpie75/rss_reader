from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login

admin.autodiscover()

urlpatterns=[
	# Examples:
	url(r'^feeds/', include('feeds.urls')),
	url(r'^$', include('viewer.urls')),
	url(r'^login/$', login, {'template_name':'login.jinja'}),
	# url(r'^rss/', include('rss.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
]
