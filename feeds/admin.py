from django.contrib import admin
from models import Feed, Article, Category


class FeedAdmin(admin.ModelAdmin):
	list_display=('title', 'last_fetched', 'last_updated')
	actions=['force_update', 'update_favicon']

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


class ArticleAdmin(admin.ModelAdmin):
	list_display=('feed', 'date_published', 'title', 'read')
	list_editable=('read',)
	list_filter=('read', 'feed')
	actions=['mark_read',]

	def mark_read(self, request, qs):
		num_articles=len(qs)
		qs.update(read=True)
		if num_articles==1:
			message='1 article was'
		else:
			message='{} articles were'.format(num_articles)
		self.message_user(request, '{} marked as read'.format(message))
	mark_read.short_description='Mark selected articles as read'


class CategoryAdmin(admin.ModelAdmin):
	list_display=('name', 'parent')

admin.site.register(Feed, FeedAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
