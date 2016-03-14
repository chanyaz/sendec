from django.db import models
from django.contrib.auth.models import User


class UserReports(models.Model):
    class Meta:
        db_table = "user_reports"
        verbose_name = "Report"
        verbose_name_plural = "Reports"

    user = models.ForeignKey(User, related_name="report")
    email_new = models.EmailField(max_length=128, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=False)

    rss = models.BooleanField(default=False, blank=False)
    portal_link = models.URLField(default="", blank=False)

    news = models.BooleanField(default=False, blank=False)
    design = models.BooleanField(default=False, blank=False)
    error = models.BooleanField(default=False, blank=False)
    localization = models.BooleanField(default=False, blank=False)


    def __str__(self):
        return self.user.username