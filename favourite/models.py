from django.db import models
from django.contrib.auth.models import User
from news.models import RssNews


class RssSaveNews(models.Model):
    class Meta:
        db_table = "rss_save"
        verbose_name = "RSS"
        verbose_name_plural = "RSS"

    user = models.ForeignKey(User)
    rss = models.ForeignKey(RssNews, related_name="rss_article")

    def __str__(self):
        return self.rss.title