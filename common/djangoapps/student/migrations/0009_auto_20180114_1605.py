# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_auto_20161117_1209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='languageproficiency',
            name='code',
            field=models.CharField(help_text='The ISO 639-1 language code for this language.', max_length=16, choices=[['an', 'Aragon\xe9s'], ['eu', 'Euskera'], ['ca', 'Catal\xe1n'], ['en', 'Ingl\xe9s'], ['fr', 'Franc\xe9s'], ['gl', 'Gallego'], ['pt', 'Portugu\xe9s'], ['es', 'Espa\xf1ol']]),
        ),
    ]
