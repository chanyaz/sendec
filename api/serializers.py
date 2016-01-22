from django.contrib.auth.models import User, Group
from rest_framework import serializers
from news.models import News


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News