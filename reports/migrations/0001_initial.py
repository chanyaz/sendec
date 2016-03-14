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
            name='UserReports',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('email_new', models.EmailField(max_length=128, blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('rss', models.BooleanField(default=False)),
                ('portal_link', models.URLField(default='')),
                ('news', models.BooleanField(default=False)),
                ('design', models.BooleanField(default=False)),
                ('error', models.BooleanField(default=False)),
                ('localization', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='report')),
            ],
            options={
                'verbose_name': 'Report',
                'db_table': 'user_reports',
                'verbose_name_plural': 'Reports',
            },
        ),
    ]
