from django.db import models
from django.contrib.auth.models import User


def upload_user_photo(instance, filename):
    return "/".join(["content", "users", instance.user.username, "photos", filename])


class UserProfile(models.Model):
    class Meta:
        db_table = "user_profile"

    user = models.OneToOneField(User, related_name="profile")
    user_photo = models.FileField(upload_to=upload_user_photo)
    user_cell_number = models.TextField(max_length=11)
    written_articles = models.IntegerField(default=0)
    user_rate = models.FloatField(default=0.0)

    confirmation_code = models.CharField(max_length=33)
