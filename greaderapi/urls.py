from django.conf.urls import url
from .views import user_info, unread_count, subscription_list, subscription_edit, subscription_quickadd
from .views import tag_list, tag_rename, tag_delete, tag_edit, stream_contents

urlpatterns=[
	url(r'^reader/api/0/user-info$', user_info, name='user_info'),
	url(r'^reader/api/0/unread-count$', unread_count, name='unread_count'),
	url(r'^reader/api/0/stream/contents/(?P<stream>.*?)$', stream_contents, name='stream_contents'),
	# url(r'^reader/api/0/stream/items/ids$', streams_item_ids, name='streams_item_ids'),
	url(r'^reader/api/0/subscription/quickadd$', subscription_quickadd, name='subscription_quickadd'),
	url(r'^reader/api/0/subscription/edit$', subscription_edit, name='subscription_edit'),
	url(r'^reader/api/0/subscription/list$', subscription_list, name='subscription_list'),
	url(r'^reader/api/0/tag/list$', tag_list, name='tag_list'),
	url(r'^reader/api/0/rename-tag$', tag_rename, name='tag_rename'),
	url(r'^reader/api/0/disable-tag$', tag_delete, name='tag_delete'),
	url(r'^reader/api/0/edit-tag$', tag_edit, name='tag_edit'),
]
