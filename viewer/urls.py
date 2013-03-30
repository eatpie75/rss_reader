from django.conf.urls import patterns, url

urlpatterns=patterns('',
	# Examples:
	url(r'^$', 'viewer.views.index', name='index'),
	# url(r'^rss/', include('rss.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	# url(r'^admin/', include(admin.site.urls)),
)
