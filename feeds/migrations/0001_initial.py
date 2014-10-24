# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('guid', models.TextField(db_index=True)),
                ('title', models.TextField()),
                ('author', models.CharField(max_length=250, blank=True)),
                ('date_added', models.DateTimeField()),
                ('date_published', models.DateTimeField()),
                ('date_updated', models.DateTimeField()),
                ('date_last_seen', models.DateTimeField()),
                ('description', models.TextField(blank=True)),
                ('content', models.TextField(blank=True)),
                ('url', models.URLField(max_length=500)),
            ],
            options={
                'ordering': ['-date_published', '-date_added', '-id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('parent', models.ForeignKey(blank=True, to='feeds.Category', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(db_index=True, serialize=False, primary_key=True)),
                ('title', models.TextField(blank=True)),
                ('feed_url', models.URLField(max_length=500)),
                ('site_url', models.URLField(max_length=500, null=True, blank=True)),
                ('feed_image', models.ImageField(null=True, upload_to=b'feeds', blank=True)),
                ('date_added', models.DateTimeField(null=True, blank=True)),
                ('last_fetched', models.DateTimeField(null=True, blank=True)),
                ('last_updated', models.DateTimeField(null=True, blank=True)),
                ('update_interval', models.IntegerField(default=300, help_text=b'Base time between updates in minutes')),
                ('next_fetch', models.DateTimeField(null=True, blank=True)),
                ('purge_interval', models.IntegerField(default=0)),
                ('enabled', models.BooleanField(default=True)),
                ('success', models.BooleanField(default=True)),
                ('last_error', models.CharField(max_length=500, blank=True)),
                ('statistics', jsonfield.fields.JSONField(default={})),
                ('statistics_updated', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ['title'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserArticleInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('read', models.BooleanField(default=False, db_index=True)),
                ('date_read', models.DateTimeField(null=True, blank=True)),
                ('article', models.ForeignKey(to='feeds.Article')),
            ],
            options={
                'ordering': ['-article__date_published', '-article__date_added', '-article__id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserFeedCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unread', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserFeedSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(blank=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, to='feeds.Category', null=True)),
                ('feed', models.ForeignKey(to='feeds.Feed')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['feed__title'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='userfeedsubscription',
            unique_together=set([('user', 'feed')]),
        ),
        migrations.AddField(
            model_name='userfeedcache',
            name='feed',
            field=models.ForeignKey(to='feeds.UserFeedSubscription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userfeedcache',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='userfeedcache',
            unique_together=set([('user', 'feed')]),
        ),
        migrations.AlterIndexTogether(
            name='userfeedcache',
            index_together=set([('user', 'feed')]),
        ),
        migrations.AddField(
            model_name='userarticleinfo',
            name='feed',
            field=models.ForeignKey(to='feeds.UserFeedSubscription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userarticleinfo',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='userarticleinfo',
            unique_together=set([('user', 'feed', 'article')]),
        ),
        migrations.AlterIndexTogether(
            name='userarticleinfo',
            index_together=set([('user', 'feed', 'read'), ('user', 'feed')]),
        ),
        migrations.AddField(
            model_name='article',
            name='feed',
            field=models.ForeignKey(to='feeds.Feed'),
            preserve_default=True,
        ),
    ]
