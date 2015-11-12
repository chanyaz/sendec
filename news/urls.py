from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    # Likes
    url(r'^add_like/n=(?P<news_id>\w+)', 'news.views.add_like_news'),
    url(r'^check_like/n=(?P<news_id>\w+)', 'news.views.check_like_amount'),

    # Dislikes
    url(r'^add_dislike/n=(?P<news_id>\w+)', 'news.views.add_dislike_news'),
    url(r'^check_dislike/n=(?P<news_id>\w+)', 'news.views.check_dislike_amount'),


    url(r'^comments=(?P<category_id>\w+)&(?P<news_id>\w+)/', 'news.views.render_current_news_comments'),
    url(r'^send/cat=(?P<category_id>\w+)&id=(?P<news_id>\w+)/', 'news.views.comment_send'),
    url(r'^reply/nid=(?P<news_id>\w+)&cid=(?P<comment_id>\w+)/', 'news.views.reply_send'),
    url(r'^(?P<category_id>\w+)/(?P<news_id>\w+)/', 'news.views.render_current_news'),
    url(r'^(?P<category_name>\w+)/', 'news.views.render_current_category'),
]
