from django.db import models
from loginsys.models import UserProfile
from django.contrib.auth.models import User

# Create your models here.


class NewsCategory(models.Model):
    class Meta:
        db_table = "news_category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    category_name = models.CharField(max_length=16)

    def __str__(self):
        return self.category_name


class NewsPortal(models.Model):
    class Meta:
        db_table = "news_portal"
        verbose_name = "Portal"
        verbose_name_plural = "Portals"

    portal_name = models.CharField(max_length=32)

    def __str__(self):
        return self.portal_name


class News(models.Model):
    class Meta:
        db_table = "news"
        verbose_name = "News"
        verbose_name_plural = "News"

    news_title = models.CharField(max_length=128)
    news_category = models.ForeignKey(NewsCategory)
    news_post_date = models.DateTimeField(auto_now_add=True)
    news_post_text = models.TextField(max_length=4096)
    news_portal_name = models.ForeignKey(NewsPortal)

    news_latest_shown = models.BooleanField(default=False)
    news_currently_showing = models.BooleanField(default=False)

    # Media
    # news_main_cover = models.FileField(upload_to='', storage=None)

    # Information
    news_likes = models.IntegerField(default=0)
    news_dislikes = models.IntegerField(default=0)

    news_event = models.BooleanField(default=False)
    news_event_date = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.news_title

    def get_portal_name(self, portal_id):
        return NewsPortal.objects.get(id=portal_id).portal_name

    def get_category_name(self, category_id):
        return NewsCategory.objects.get(id=category_id).category_name


    def get_json_comments_replies(self):
        return {
            "news_id": self.id,
            "comments": NewsComments.objects.filter(news_attached=self.id),
            "replies": NewsCommentsReplies.objects.filter(news_attached=self.id),
        }

    def get_json_news(self):
        return {
            "news_id": self.id,
            "news_title": self.news_title,
            "news_post_date": self.news_post_date.time().isoformat(),
            "shown": self.news_latest_shown,
            "show_now": self.news_currently_showing,
        }


class NewsWatches(models.Model):
    class Meta:
        db_table = "news_watches"

    news = models.ForeignKey(News, related_name="watches")
    watches = models.IntegerField(default=0)
    external_transition = models.IntegerField(default=0)


class NewsComments(models.Model):
    class Meta:
        db_table = "news_comments"
        verbose_name = "comment"
        verbose_name_plural = "comments"

    news_attached = models.ForeignKey(News)
    comments_author = models.ForeignKey(User)
    comments_text = models.TextField(max_length=512)
    comments_post_date = models.DateTimeField(auto_now_add=True)
    comments_likes = models.IntegerField(default=0)
    comments_dislikes = models.IntegerField(default=0)


    def get_json_comments(self):
        return {
            "comments_id": self.id,
            "comments_news_attached": self.news_attached.id,
            "comments_author": self.comments_author.username,
            "comments_text": self.comments_text,
            "comments_post_date": self.comments_post_date.date().isoformat(),
            "comments_post_time": self.comments_post_date.time().isoformat(),
            "comments_likes": self.comments_likes,
            "comments_dislikes": self.comments_dislikes
        }


class NewsCommentsReplies(models.Model):
    class Meta:
        db_table = "news_comments_replies"

    comment_attached = models.ForeignKey(NewsComments)
    news_attached = models.ForeignKey(News)

    reply_author = models.ForeignKey(User)
    reply_text = models.TextField(max_length=512)
    reply_post_date = models.DateTimeField(auto_now_add=True)
    reply_likes = models.IntegerField(default=0)
    reply_dislikes = models.IntegerField(default=0)


    def get_json_replies(self):
        return {
            "replies_id": self.id,
            "replies_comments_attached": self.comment_attached.id,
            "replies_news_attached": self.news_attached.id,
            "replies_author": self.reply_author.username,
            "replies_text": self.reply_text,
            "replies_post_date": self.reply_post_date.date().isoformat(),
            "replies_post_hour": self.reply_post_date.time().isoformat(),
            "replies_likes": self.reply_likes,
            "replies_dislikes": self.reply_dislikes
        }


class RssNews(models.Model):
    class Meta:
        db_table = "news_rss"

    title = models.CharField(max_length=128)
    date_posted = models.DateTimeField(auto_now_add=True)
    post_text = models.TextField(max_length=4096)
    portal_name = models.ForeignKey(NewsPortal)
    category = models.ForeignKey(NewsCategory)
    link = models.URLField(max_length=128)
