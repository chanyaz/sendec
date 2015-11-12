from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserProfile(models.Model):
    class Meta:
        db_table = "user_profile"

    user = models.OneToOneField(User)

