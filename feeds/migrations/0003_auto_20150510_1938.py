# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0002_category_expanded'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userfeedsubscription',
            options={'ordering': ['title']},
        ),
    ]
