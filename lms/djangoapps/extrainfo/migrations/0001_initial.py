# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NationalId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('national_id', models.CharField(max_length=30, unique=True, verbose_name=b'National Identification Number', error_messages={b'required': 'Please introduce your National ID number', b'invalid': "National ID number isn valid", b'unique':"Already exists"})),
                ('user', models.OneToOneField(null=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
