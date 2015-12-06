from django.db import models
from django.contrib.auth.models import User


class UserRequests(models.Model):
    class Meta:
        db_table="user_requests"
        verbose_name="request"
        verbose_name_plural="requests"
    user=models.ForeignKey(User)
    request=models.CharField(max_length=1024)