# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Feed'
        db.create_table(u'feeds_feed', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('feed_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('site_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('update_interval', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('purge_interval', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'feeds', ['Feed'])

        # Adding model 'Article'
        db.create_table(u'feeds_article', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('date_published', self.gf('django.db.models.fields.DateField')()),
            ('date_updated', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('read', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'feeds', ['Article'])


    def backwards(self, orm):
        # Deleting model 'Feed'
        db.delete_table(u'feeds_feed')

        # Deleting model 'Article'
        db.delete_table(u'feeds_article')


    models = {
        u'feeds.article': {
            'Meta': {'object_name': 'Article'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_published': ('django.db.models.fields.DateField', [], {}),
            'date_updated': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
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
            'last_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'purge_interval': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'site_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'update_interval': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['feeds']