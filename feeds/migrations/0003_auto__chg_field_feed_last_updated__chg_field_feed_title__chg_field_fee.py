# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Feed.last_updated'
        db.alter_column(u'feeds_feed', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Feed.title'
        db.alter_column(u'feeds_feed', 'title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'Feed.site_url'
        db.alter_column(u'feeds_feed', 'site_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True))

        # Changing field 'Article.feed'
        db.alter_column(u'feeds_article', 'feed_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feeds.Feed']))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Feed.last_updated'
        raise RuntimeError("Cannot reverse this migration. 'Feed.last_updated' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Feed.title'
        raise RuntimeError("Cannot reverse this migration. 'Feed.title' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Feed.site_url'
        raise RuntimeError("Cannot reverse this migration. 'Feed.site_url' and its values cannot be restored.")

        # Changing field 'Article.feed'
        db.alter_column(u'feeds_article', 'feed_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feeds.Feed'], null=False))

    models = {
        u'feeds.article': {
            'Meta': {'object_name': 'Article'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_published': ('django.db.models.fields.DateField', [], {}),
            'date_updated': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feeds.Feed']"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'feeds.feed': {
            'Meta': {'object_name': 'Feed'},
            'feed_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'purge_interval': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'site_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'update_interval': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['feeds']