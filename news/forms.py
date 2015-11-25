from django import forms
from .models import News, NewsComments, NewsCommentsReplies
from django.forms import ModelForm


class NewsCommentsForm(ModelForm):
    class Meta:
        model = NewsComments
        fields = ["comments_text"]


class NewsCommentsRepliesForm(ModelForm):
    class Meta:
        model = NewsCommentsReplies
        fields = ["reply_text"]
