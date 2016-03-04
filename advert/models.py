from django.db import models
from django.contrib.auth.models import User


def upload_advert_data(instance, filename):
    return '/'.join(['media', 'advert', instance.owner.username, filename])


class Advertisement(models.Model):
    class Meta:
        db_table = "advert"

    owner = models.ForeignKey(User)
    name = models.CharField(max_length=32, blank=False)
    data = models.FileField(upload_to=upload_advert_data, blank=False)


class AdvertClicks(models.Model):
    class Meta:
        db_table = "advert_clicks"

    advert = models.ForeignKey(Advertisement, related_name="ad_clicks")
    clicks = models.IntegerField(default=0)


class AdvertViews(models.Model):
    class Meta:
        db_table = "advert_views"
    advert = models.ForeignKey(Advertisement, related_name="ad_views")
    views = models.IntegerField(default=0)


class AdvertCTR(models.Model):
    class Meta:
        db_table = "advert_ctr"
    advert = models.ForeignKey(Advertisement, related_name="ctr")
    ctr = models.FloatField(default=.0)


class AdvertBudget(models.Model):
    class Meta:
        db_table = "advert_budget"
    advert = models.ForeignKey(Advertisement, related_name="ad_budget")
    budget = models.FloatField(default=.0)
