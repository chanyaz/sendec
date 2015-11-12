from django.db import models
from loginsys.models import UserProfile
from django.contrib.auth.models import User


class UserSettings(models.Model):
    class Meta:
        db_table = "user_settings"
        verbose_name = "Setting"
        verbose_name_plural = "Settings"

    user = models.ForeignKey(User)
    color_scheme = models.TextField(max_length=9)

    def __str__(self):
        return self.user.username