from django.db import models
from loginsys.models import UserProfile
from django.contrib.auth.models import User
#import PIL
#from PIL import Image
#from imagekit.models.fields import ImageSpecField
#from imagekit.processors import ResizeToFit, Adjust,ResizeToFill
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
# from favourite.models import RssSaveNews
from django.contrib.postgres.fields import ArrayField
from djorm_pgarray.fields import ArrayField




def upload_news_cover(instance, filename):
        return "/".join(["content", "news", "covers", filename])

def upload_company_cover(instance, filename):
    return "/".join(["content", "companies", "logo", filename])


def upload_rss_portals_covevrs(instance, filename):
    return "/".join(["content", "rss", "portals", 'covers', filename])


def upload_rss_favicon(instance, filename):
    return "/".join(['content', 'rss', 'portals', 'favicons', filename])


def upload_main_rss_portal_cover(instance, filename):
    return "/".join(["content", "rss", "portals", "main_covers", filename])


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
    portal_base_link = models.CharField(max_length=128)

    def __str__(self):
        return self.portal_name


class Companies(models.Model):
    class Meta:
        db_table = 'companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    name = models.CharField(max_length=64)
    verbose_name = models.CharField(max_length=64)
    site = models.URLField(max_length=64)
    category = models.ForeignKey(NewsCategory)
    logo = models.FileField(upload_to=upload_company_cover, blank=True)

    description = models.TextField(max_length=4096)


    def __str__(self):
        return self.name

    def get_json_company_suggest(self):
        return {
            "id": self.id,
            "name": self.name,
            "verbose": self.verbose_name,
            "logo": str(self.logo)
        }

    def get_absolute_url(self):
        return "/news/companies/%s/" % self.verbose_name



class News(models.Model):
    class Meta:
        db_table = "news"
        verbose_name = "News"
        verbose_name_plural = "News"

    news_title_english = models.CharField(max_length=512)
    news_title_russian = models.CharField(max_length=512)
    news_title_chinese = models.CharField(max_length=512)
    news_category = models.ForeignKey(NewsCategory)
    news_post_date = models.DateTimeField(auto_now_add=True)

    teaser_english = models.TextField(max_length=512)
    teaser_russian = models.TextField(max_length=512)
    teaser_chinese = models.TextField(max_length=512)

    news_post_text_english = models.TextField(max_length=4096, blank=True, default="Empty")
    news_post_text_russian = models.TextField(max_length=4096, blank=True, default="Empty")
    news_post_text_chinese = models.TextField(max_length=4096, blank=True, default="Empty")

    news_portal_name = models.ForeignKey(NewsPortal, blank=True, related_name="portal")
    news_company_owner = models.ForeignKey(Companies, blank=True, related_name="company")
    news_author = models.ForeignKey(User, blank=True, related_name="author")

    # Media
    news_main_cover = models.FileField(upload_to=upload_news_cover, blank=True)

    photo = models.ImageField(upload_to=upload_news_cover, blank=True)
    # photo_small = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1), ResizeToFill(50, 50)],# image_field='photo',
    #                             format='JPEG', options={'quality': 90})
    # photo_medium = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1), ResizeToFit(300, 200)],# image_field='photo',
    #                              format='JPEG', options={'quality': 90})
    # photo_big = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1), ResizeToFit(640, 480)],# image_field='photo',
    #                           format='JPEG', options={'quality': 90})



    # Information
    news_likes = models.IntegerField(default=0)
    news_dislikes = models.IntegerField(default=0)
    news_tags = ArrayField(dbtype="varchar(255)")
    slug = models.SlugField(max_length=256, unique=True, blank=True)

    def get_absolute_url(self):
        # URL is /{year}/{month}/{day}/{slug}
        # return "/news/%s/%s" % (self.news_category_id, self.id)
        # return reverse('news.views.render_current_news', args=[str(self.slug)])
        return "/news/%s/%s/%s/%s/%s" % (self.news_post_date.year,
                             self.news_post_date.month,
                             self.news_post_date.day,
                             self.id,
                             str(self.slug))



    def get_news_id(self):
        return self.id

    def __str__(self):
        return self.news_title_english

    # def __unicode__(self):
    #     return self.news_post_text_russian

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
    def get_json_for_search(self):
        return {
            'id': self.id,
            'title': self.news_title,
            'category': self.news_category_id,
            'cover': str(self.news_main_cover)
        }
    #
    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.s = slugify(self.news_title)
    #     super(News, self).save(*args, **kwargs)


class TopNews(models.Model):
    class Meta:
        db_table = "news_top"
        verbose_name = "Top"
        verbose_name_plural = "Top news"

    top_news_title_english = models.CharField(max_length=512, blank=False)
    top_news_title_russian = models.CharField(max_length=512, blank=True)
    top_news_title_chinese = models.CharField(max_length=512, blank=True)
    top_news_category = models.ForeignKey(NewsCategory)
    top_news_post_date = models.DateTimeField(auto_now_add=True)

    teaser_english = models.TextField(max_length=128, blank=False)
    teaser_russian = models.TextField(max_length=128, blank=False)
    teaser_chinese = models.TextField(max_length=128, blank=False)

    top_news_post_text_english = models.TextField(max_length=4096)
    top_news_post_text_russian = models.TextField(max_length=4096)
    top_news_post_text_chinese = models.TextField(max_length=4096)

    top_news_portal_name = models.ForeignKey(NewsPortal, blank=True)
    top_news_company_owner = models.ForeignKey(Companies, blank=True)
    top_news_author = models.ForeignKey(User, blank=True)

    # Media
    top_news_main_cover = models.FileField(upload_to=upload_news_cover, blank=True)

    # Information
    top_news_likes = models.IntegerField(default=0)
    top_news_dislikes = models.IntegerField(default=0)

    slug = models.SlugField(max_length=256, unique=True, blank=True)


    def __str__(self):
        return self.top_news_title_english

    def get_absolute_url(self):
        return "news/top/%s/%s" % (self.id, str(self.slug))


class NewsWatches(models.Model):
    class Meta:
        db_table = "news_watches"

    news = models.ForeignKey(News, related_name="watches")
    watches = models.IntegerField(default=0)
    external_transition = models.IntegerField(default=0)

    def __str__(self):
        return self.news.news_title


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


class RssPortals(models.Model):
    class Meta:
        db_table = "rss_portals"

    portal = models.CharField(max_length=128)
    portal_base_link = models.CharField(max_length=128)
    follows = models.IntegerField(default=0)
    description = models.TextField(max_length=1024)
    cover = models.CharField(max_length=512)
    # favicon = models.FileField(upload_to=upload_rss_favicon, blank=True)
    favicon = models.TextField(max_length=512, blank=True)
    verbose_name = models.CharField(max_length=128)
    category = models.ForeignKey(NewsCategory)
    main_portal_cover = models.FileField(upload_to=upload_main_rss_portal_cover, blank=True)
    # feed_url = models.URLField(max_length=256)

    puid = models.UUIDField(max_length=33, unique=True)


    def __str__(self):
        return self.portal

    def get_json(self):
        return {
            'id': self.id,
            'portal': self.portal,
            'verbose': self.verbose_name,
            'favicon': self.favicon,
        }

    def get_portal_full(self):
        return {
            "id": self.id,
            "portal": self.portal,
            "link": self.portal_base_link,
            "follows": self.follows,
            "description": self.description,
            "cover": str(self.cover),
            "favicon": self.favicon,
            "verbose": self.verbose_name,
            "category": self.category_id,
        }


class RSSChannels(models.Model):
    class Meta:
        db_table = "rss_channels"
        verbose_name = "Rss channel"
        verbose_name_plural = "Rss channels"

    portal = models.ForeignKey(RssPortals, related_name="channel")
    link = models.URLField(max_length=256)

    def __str__(self):
        return self.portal.portal


class RssNews(models.Model):
    class Meta:
        db_table = "news_rss"

    title = models.CharField(max_length=512)
    date_posted = models.DateTimeField(auto_now_add=True)
    post_text = models.TextField(max_length=4096)
    portal_name = models.ForeignKey(RssPortals)
    #portal_name_rate = models.ForeignKey(RssPortals, related_name="rate")
    category = models.ForeignKey(NewsCategory)
    link = models.URLField(max_length=512)
    author = models.CharField(max_length=512)
    content_value = models.TextField(max_length=16384)

    nuid = models.CharField(max_length=33)

    def __str__(self):
        return self.title

    #def __unicode__(self):
    #    return self.post_text, self.content_value

    #def __repr__(self):
    #    return self.post_text.encode("utf-8")

    def get_json_rss(self):
        return {
            "id": self.id,
            "nuid": self.nuid,
            "title": self.title,
            "date": self.date_posted.date().isoformat(),
            "time": self.date_posted.time().isoformat(),
            "text": self.post_text,
            "portal": self.portal_name_id,
            "category": self.category_id,
            "link": self.link,
            "content": self.content_value,#.replace("\u2019", "&rsquo;"),
            "author": self.author,
            "cover": self.get_main_cover(),
            "fav": self.get_rss_fav(),
        }

    def get_rss_fav(self):
        from favourite.models import RssSaveNews
        rss_instance = RssSaveNews.objects.filter(rss_id=self.id)
        try:
            if rss_instance.exists() == True:
                return True
            else:
                return False
        except RssSaveNews.objects.get(rss_id=self.id).DoesNotExist:
            return False

    def get_portal_json(self):
        return {
            "id": self.portal_name_id,
            "name": str(RssPortals.objects.get(id=self.portal_name_id).portal)
        }

    def get_main_cover(self):
        try:
            return str(RssNewsCovers.objects.get(rss_news_id=self.id).main_cover)
        except RssNewsCovers.DoesNotExist:
            return ""


class UserRssNewsReading(models.Model):
    class Meta:
        db_table = "user_rss_news_read"

    user = models.ForeignKey(User, related_name="read")
    rss_news = models.ForeignKey(RssNews, related_name="read_rss")
    rss_portal = models.ForeignKey(RssPortals)
    read = models.BooleanField(default=False)


class RssNewsCovers(models.Model):
    class Meta:
        db_table = "rss_news_covers"
    rss_news = models.ForeignKey(RssNews, related_name="rss_covers")
    main_cover = models.TextField(max_length=512)

    def __str__(self):
        return self.rss_news.portal_name.portal


class TopVideoContent(models.Model):
    class Meta:
        db_table = "video_top"
        verbose_name = "video"
        verbose_name_plural = "videos"

    video = models.URLField()
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class SubscriptionUsers(models.Model):
    class Meta:
        db_table = "closet_subs"

    email = models.EmailField(max_length=128)
    uid = models.UUIDField(max_length=33)


class UserSearchPortals(models.Model):
    class Meta:
        db_table = "search_rss_user"
    name = models.CharField(max_length=64,blank=False)
    url = models.CharField(max_length=128,blank=False)
    link = models.TextField(max_length=1024,blank=False)
    date = models.DateTimeField(auto_now_add=True,blank=False)