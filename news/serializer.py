from rest_framework import serializers

from news.models import News


from django.utils.html import strip_tags


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('id', 'news_title', 'news_post_date', 'news_post_text_english', 'news_portal_name', 'news_company_owner',
                  'news_author')

