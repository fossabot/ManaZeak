# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-25 11:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_playlist_refreshview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='location',
            field=models.FilePathField(max_length=1000, unique=True),
        ),
    ]
