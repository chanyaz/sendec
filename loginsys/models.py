from django.db import models
from django.contrib.auth.models import User


def upload_user_photo(instance, filename):
    return "/".join(["media", "users", instance.user.username, "photos", filename])


class UserProfile(models.Model):
    class Meta:
        db_table = "user_profile"

    user = models.ForeignKey(User)
    user_photo = models.FileField(upload_to=upload_user_photo)

