from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^cl&t=0&id=(?P<news_id>\w+)&lang_code=(?P<lang_code>\w+)', 'news.views.change_languages'),
    url(r'^cl&t=1&id=(?P<news_id>\w+)&lang_code=(?P<lang_code>\w+)', 'news.views.change_languages_top_news'),
    url(r'^change_portals_order/', 'news.views.change_rates'),
    url(r'^add_portals/', 'news.views.set_user_portals'),
    url(r'^about/', 'news.views.render_about_page'),
    url(r'^contacts/', 'news.views.render_contacts_page'),
    url(r'^advertisers/', 'news.views.render_adertisers_page'),
    url(r'^send_report/', 'news.views.send_report'),
    url(r"^test_rendering/", "news.views.test_rendering"),

    url(r'^update_user_rss_news/', 'news.views.get_updated_rss'),
    url(r'^update_user_rss/', 'news.views.get_updated_user_rss'),
    url(r'^gcr=(?P<news_id>\w+)/', 'news.views.get_current_rss_news'),

    # External Transitions
    #url(r"^trans/(?P<cat_id>\w+)/(?P<news_id>\w+)/", 'news.views.external_transition'),
    url(r'^new_page/cp=(?P<current_page>\w+)&np=(?P<next_page>\w+)/', 'news.views.get_rss_news_pagination'),


    url(r'^companies/(?P<company_name>\w+)/', 'news.views.render_current_company'),


    # Likes
    url(r'^add_like/n=(?P<news_id>\w+)', 'news.views.add_like_news'),
    url(r'^add_like_rss/r=(?P<rss_id>\w+)', 'news.views.save_rss_news'),
    url(r'^check_like/n=(?P<news_id>\w+)', 'news.views.check_like_amount'),


    # Dislikes
    url(r'^add_dislike/n=(?P<news_id>\w+)', 'news.views.add_dislike_news'),
    url(r'^check_dislike/n=(?P<news_id>\w+)', 'news.views.check_dislike_amount'),

    # Latest news
    url(r'^update_latest/', "news.views.update_latest_news"),
    url(r'^ss=(?P<news_id>\w+)','news.views.set_shown'),


    # Deleting objects
    #url(r'^cd=(?P<comment_id>\w+)/', 'news.views.delete_comment'),
    #url(r'^rd=(?P<reply_id>\w+)/', 'news.views.delete_reply'),


    #url(r'^comments=(?P<category_id>\w+)&(?P<news_id>\w+)/', 'news.views.render_current_news_comments'),
    url(r'^send/cat=(?P<category_id>\w+)&id=(?P<news_id>\w+)/', 'news.views.comment_send'),
    url(r'^reply/nid=(?P<news_id>\w+)&cid=(?P<comment_id>\w+)/', 'news.views.reply_send'),
    url(r"^load=(?P<news_id>\w+)", "news.views.comments_load"),

    # Top news
    # url(r'^top/', "news.views.render_top_news_page"),


    # User RSS news
    #url(r'^usernews/', 'news.views.render_user_news'),
    #url(r'^usernews/(?P<portal_verbose>\w+)', 'news.views.get_rss_news_current_portal'),
    url(r'^usernews/page/(?P<portal>\w+)', 'news.views.render_current_portal_news'),
    url(r'^usernews/', 'news.views.render_user_news'),



    url(r'^top/(?P<category_id>\w+)/(?P<news_id>\w+)/', 'news.views.render_current_top_news'),
    url(r'^top/translate/', 'news.views.translate_news_from_top'),

    url(r'^(?P<category_id>\w+)/(?P<news_id>\w+)/', 'news.views.render_current_news'),
    #url(r'^(?P<category_name>\w+)/', 'news.views.render_current_category'),
    url(r'^auto/', 'news.views.render_auto_news'),
    url(r'^bio/', 'news.views.render_bio_news'),

    url(r'^companies/cs=(?P<company>\w+)', 'news.views.get_match_company'),
    url(r'^companies/', 'news.views.render_companies_news'),
    # url(r'^/blink-to-company/(?P<company_name>\w+)', 'news.views.blink_to_company'),
    # url(r'^comp/gid=(?P<company_verbose>\w+)', 'news.views.get_company_id'),


    url(r'^entertainment/', 'news.views.render_entertainment_news'),
    url(r'^technology/', 'news.views.render_technology_news'),
    url(r'^latest/', 'news.views.render_latest_news'),
    url(r'^reviews/', 'news.views.render_reviews_news'),
    url(r'^rrp&uid=(?P<uuid>[^/]+)&pid=(?P<pid>\w+)/', 'news.views.remove_rss_portal_from_feed'),
    url(r'^space/', 'news.views.render_space_news'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
