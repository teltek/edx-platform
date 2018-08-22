# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0004_badgeclass_badgr_server_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgeclass',
            name='badgr_server_slug',
            field=models.SlugField(default=b'', max_length=255, blank=True),
        ),
    ]
