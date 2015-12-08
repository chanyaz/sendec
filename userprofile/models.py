from django.db import models
from loginsys.models import UserProfile
from django.contrib.auth.models import User
from news.models import News, NewsCategory, NewsPortal, RssPortals


class UserSettings(models.Model):
    class Meta:
        db_table = "user_settings"
        verbose_name = "Setting"
        verbose_name_plural = "Settings"

    user = models.ForeignKey(User)
    color_scheme = models.TextField(max_length=9)
    portals_to_show = models.TextField(max_length=256)
    categories_to_show = models.TextField(max_length=64)

    def __str__(self):
        return self.user.username


class UserLikesNews(models.Model):
    class Meta:
        db_table = "user_likes_news"

    user = models.ForeignKey(User)
    news = models.ForeignKey(News)
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)


class UserRssPortals(models.Model):
    class Meta:
        db_table = "user_rss_news"

    user = models.ForeignKey(User, related_name="user_rss")
    portal = models.ForeignKey(RssPortals)
    check = models.BooleanField(default=False)

    def get_json_portal(self):
        return {
            "id": self.portal_id,
            "cur_user": str(self.user.profile.serializable_value("uuid")),
            "del_item": "<span onclick='/news/rrp&uid=%s&pid=%s/'>X</span>" % (self.user.profile.uuid, self.id),
            "name": RssPortals.objects.get(id=self.portal_id).portal,
            "check": self.check
        }