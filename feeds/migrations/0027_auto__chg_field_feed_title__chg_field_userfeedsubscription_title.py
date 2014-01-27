# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Feed.title'
        db.alter_column(u'feeds_feed', 'title', self.gf('django.db.models.fields.CharField')(max_length=500))

        # Changing field 'UserFeedSubscription.title'
        db.alter_column(u'feeds_userfeedsubscription', 'title', self.gf('django.db.models.fields.CharField')(max_length=500))

    def backwards(self, orm):

        # Changing field 'Feed.title'
        db.alter_column(u'feeds_feed', 'title', self.gf('django.db.models.fields.CharField')(max_length=200))

        # Changing field 'UserFeedSubscription.title'
        db.alter_column(u'feeds_userfeedsubscription', 'title', self.gf('django.db.models.fields.CharField')(max_length=200))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'feeds.article': {
            'Meta': {'ordering': "['-date_published', '-date_added', '-id']", 'object_name': 'Article'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {}),
            'date_last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feeds.Feed']"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'feeds.category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feeds.Category']", 'null': 'True', 'blank': 'True'})
        },
        u'feeds.feed': {
            'Meta': {'ordering': "['title']", 'object_name': 'Feed'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feeds.Category']", 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'feed_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'feed_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_index': 'True'}),
            'last_error': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'last_fetched': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'next_fetch': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'purge_interval': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'site_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'statistics': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'statistics_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'update_interval': ('django.db.models.fields.IntegerField', [], {'default': '300'})
        },
        u'feeds.userarticleinfo': {
            'Meta': {'ordering': "['-article__date_published', '-article__date_added', '-article__id']", 'unique_together': "[['user', 'feed', 'article']]", 'object_name': 'UserArticleInfo', 'index_together': "[['user', 'feed'], ['user', 'feed', 'read']]"},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feeds.Article']"}),
            'date_read': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feeds.Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'feeds.userfeedcache': {
            'Meta': {'unique_together': "[['user', 'feed']]", 'object_name': 'UserFeedCache', 'index_together': "[['user', 'feed']]"},
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feeds.Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'unread': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'feeds.userfeedsubscription': {
            'Meta': {'ordering': "['feed__title']", 'unique_together': "[['user', 'feed']]", 'object_name': 'UserFeedSubscription'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feeds.Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['feeds']