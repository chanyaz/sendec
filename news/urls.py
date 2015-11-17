from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    # Likes
    url(r'^add_like/n=(?P<news_id>\w+)', 'news.views.add_like_news'),
    url(r'^check_like/n=(?P<news_id>\w+)', 'news.views.check_like_amount'),

    # Dislikes
    url(r'^add_dislike/n=(?P<news_id>\w+)', 'news.views.add_dislike_news'),
    url(r'^check_dislike/n=(?P<news_id>\w+)', 'news.views.check_dislike_amount'),

    # Latest news
    url(r'^update_latest/', "news.views.update_latest_news"),
    url(r'^ss=(?P<news_id>\w+)','news.views.set_shown'),


    # Deleting objects
    url(r'^cd=(?P<comment_id>\w+)/', 'news.views.delete_comment'),
    url(r'^rd=(?P<reply_id>\w+)/', 'news.views.delete_reply'),


    url(r'^comments=(?P<category_id>\w+)&(?P<news_id>\w+)/', 'news.views.render_current_news_comments'),
    url(r'^send/cat=(?P<category_id>\w+)&id=(?P<news_id>\w+)/', 'news.views.comment_send'),
    url(r'^reply/nid=(?P<news_id>\w+)&cid=(?P<comment_id>\w+)/', 'news.views.reply_send'),


    # Top news
    url(r'^top/', "news.views.render_top_news_page"),

    # User news
    url(r'^usernews/', 'news.views.render_user_news'),

    url(r'^(?P<category_id>\w+)/(?P<news_id>\w+)/', 'news.views.render_current_news'),
    url(r'^(?P<category_name>\w+)/', 'news.views.render_current_category'),

]
