# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Article.description'
        db.alter_column(u'feeds_article', 'description', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'Article.description'
        db.alter_column(u'feeds_article', 'description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True))

    models = {
        u'feeds.article': {
            'Meta': {'object_name': 'Article'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_published': ('django.db.models.fields.DateField', [], {}),
            'date_updated': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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