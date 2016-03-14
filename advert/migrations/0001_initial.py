# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import advert.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvertBudget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('budget', models.FloatField(default=0.0)),
            ],
            options={
                'db_table': 'advert_budget',
            },
        ),
        migrations.CreateModel(
            name='AdvertClicks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('clicks', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'advert_clicks',
            },
        ),
        migrations.CreateModel(
            name='AdvertCTR',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('ctr', models.FloatField(default=0.0)),
            ],
            options={
                'db_table': 'advert_ctr',
            },
        ),
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('data', models.FileField(upload_to=advert.models.upload_advert_data)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'advert',
            },
        ),
        migrations.CreateModel(
            name='AdvertViews',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('views', models.IntegerField(default=0)),
                ('advert', models.ForeignKey(related_name='ad_views', to='advert.Advertisement')),
            ],
            options={
                'db_table': 'advert_views',
            },
        ),
        migrations.AddField(
            model_name='advertctr',
            name='advert',
            field=models.ForeignKey(related_name='ctr', to='advert.Advertisement'),
        ),
        migrations.AddField(
            model_name='advertclicks',
            name='advert',
            field=models.ForeignKey(related_name='ad_clicks', to='advert.Advertisement'),
        ),
        migrations.AddField(
            model_name='advertbudget',
            name='advert',
            field=models.ForeignKey(related_name='ad_budget', to='advert.Advertisement'),
        ),
    ]
