from datetime import datetime
from django.contrib import admin
from django import forms
from feeds.models import Feed, Article, Category, UserFeedSubscription, UserArticleInfo, UserFeedCache
from pytz import timezone


class FeedAdminForm(forms.ModelForm):
	class Meta:
		model=Feed
		exclude=()
		widgets={
			'title': forms.TextInput(),
		}


class FeedAdmin(admin.ModelAdmin):
	form=FeedAdminForm
	list_display=('title', 'enabled', 'last_fetched', 'last_updated', 'next_fetch', 'update_interval', 'time_til_fetch', 'needs_update', 'show_favicon')
	actions=['force_update', 'update_favicon', 'update_statistics']
	exclude=('statistics',)
	readonly_fields=('last_updated', 'last_error', 'statistics', 'statistics_updated', 'date_added', 'time_til_fetch', 'show_favicon')
	fieldsets=(
		(None, {
			'fields':('title', 'feed_url', 'site_url', 'show_favicon', 'feed_image')
		}), (None, {
			'fields':('date_added', 'last_fetched', 'last_updated', 'update_interval', 'next_fetch', 'time_til_fetch')
		}), (None, {
			'fields':('enabled', 'success', 'last_error')
		}), ('Statistics', {
			'classes':('collapse',),
			'fields':('statistics', 'statistics_updated')
		})
	)

	def force_update(self, request, qs):
		num_feeds=len(qs)
		for feed in qs:
			feed.update()
		if num_feeds==1:
			message='1 feed was'
		else:
			message='{} feeds were'.format(num_feeds)
		self.message_user(request, '{} updated'.format(message))
	force_update.short_description='Update selected feeds'

	def update_favicon(self, request, qs):
		i=0
		for feed in qs:
			if feed.get_favicon():
				i+=1
		self.message_user(request, '{} favicon(s) were updated'.format(i))
	update_favicon.short_description='Update favicons'

	def update_statistics(self, request, qs):
		i=0
		for feed in qs:
			feed.update_statistics()
			i+=1
		self.message_user(request, '{} feed(s) statistics were updated'.format(i))
	update_statistics.short_description='Update statistics'

	def show_favicon(self, obj):
		tmp=obj.get_feed_image
		if tmp is not None:
			return "<img src='{}'>".format(obj.get_feed_image)
		else:
			return ''
	show_favicon.allow_tags=True
	show_favicon.short_description='Favicon'

	def time_til_fetch(self, obj):
		if obj.next_fetch is not None:
			return obj.next_fetch - timezone('utc').localize(datetime.utcnow())
		else:
			return datetime(1992, 4, 26)
	time_til_fetch.short_description='Time til next fetch'


class ArticleAdmin(admin.ModelAdmin):
	list_display=('feed', 'date_published', 'title')
	list_filter=('feed',)


class CategoryAdmin(admin.ModelAdmin):
	list_display=('name', 'parent')


class UserFeedSubscriptionAdmin(admin.ModelAdmin):
	list_display=('user', 'feed', 'category')
	list_filter=('user',)
	readonly_fields=('user',)


class UserArticleInfoAdmin(admin.ModelAdmin):
	list_display=('user', 'feed', 'article_trunc', 'read', 'date_read')
	list_filter=('user', 'feed', 'read')
	readonly_fields=('user', 'feed', 'article')
	actions=['mark_read',]

	def article_trunc(self, obj):
		return obj.article.__unicode__()[:200]
	article_trunc.short_description='Article'

	def mark_read(self, request, qs):
		num_articles=len(qs)
		qs.update(read=True)
		if num_articles==1:
			message='1 article was'
		else:
			message='{} articles were'.format(num_articles)
		self.message_user(request, '{} marked as read'.format(message))
	mark_read.short_description='Mark selected articles as read'


class UserFeedCacheAdmin(admin.ModelAdmin):
	list_display=('user', 'feed', 'unread')
	readonly_fields=('user',)
	actions=['recalculate',]

	def recalculate(self, request, qs):
		for cache in qs:
			cache.recalculate()
		self.message_user(request, 'Recalculated cache(s)')
	recalculate.short_description='Recalulate cache(s)'


admin.site.register(Feed, FeedAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(UserFeedSubscription, UserFeedSubscriptionAdmin)
admin.site.register(UserArticleInfo, UserArticleInfoAdmin)
admin.site.register(UserFeedCache, UserFeedCacheAdmin)
