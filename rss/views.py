from news.models import News
from django.views.generic import TemplateView
from django.contrib.syndication.views import Feed
from django.http import HttpResponseRedirect
from news.models import Companies
import datetime
import json
import urllib.request as r


class RenderRSSPage(TemplateView):

    template_name = "rss.html"

    def get_context_data(self, **kwargs):
        context = super(RenderRSSPage, self).get_context_data()
        context['username'] = self.request.user
        context['title'] = "RSS | "
        context['latest_news'] = self.get_news_offset(offset=6)
        context['footer_news'] = self.get_news_offset(offset=3)
        if not self.request.COOKIES.get('lang'):
            region = self.get_region_code()
            if region == 'RU': context['lang'] = 'rus'
            elif region == "US": context['lang'] = 'eng'
            else: context['lang'] = 'ch'
        else:
            if 'rus' in self.request.COOKIES.get('lang'): context['lang'] = 'rus'
            elif 'eng' in self.request.COOKIES.get('lang'): context['lang'] = 'eng'
            elif 'ch' in self.request.COOKIES.get('lang'): context['lang'] = 'ch'
        return context

    def get_region_code(self):
        url = "http://ip-api.com/json"
        t = r.urlopen(url)
        data = json.loads(t.read().decode(t.info().get_param('charset') or 'utf-8'))
        return data['countryCode']

    def get_news_offset(self, offset):
        return News.objects.order_by("-news_post_date")[:offset].values()


class RssChannelLatestEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=latest&lang=eng'

    def items(self):
        return News.objects.filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelLatestChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=latest&lang=ch'

    def items(self):
        return News.objects.filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelLatestRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=latest&lang=rus'

    def items(self):
        return News.objects.filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelLatestWeekEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=latest&range=week&lang=eng'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return ["Evgeny Privalov"]

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelLatestWeekChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=latest&range=week&lang=ch'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return ["Evgeny Privalov"]

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelLatestWeekRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=latest&range=week&lang=rus'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return ["Evgeny Privalov"]

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelTechnologyEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=technology&lang=eng'

    def title(self):
        return "Technology news"

    def items(self):
        return News.objects.filter(news_category_id=1).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Technology']

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelTechnologyChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=technology&lang=ch'

    def title(self):
        return "Technology news"

    def items(self):
        return News.objects.filter(news_category_id=1).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Technology']

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelTechnologyRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=technology&lang=rus'

    def title(self):
        return "Technology news"

    def items(self):
        return News.objects.filter(news_category_id=1).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Technology']

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelTechnologyWeekEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=technology&range=week&lang=eng'

    def title(self):
        return "Technology news"

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=1).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Technology']

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelTechnologyWeekChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=technology&range=week&lang=ch'

    def title(self):
        return "Technology news"

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=1).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Technology']

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelTechnologyWeekRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=technology&range=week&lang=rus'

    def title(self):
        return "Technology news"

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=1).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Technology']

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelEntertainmentEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=entertainment&lang=eng'

    def items(self):
        return News.objects.filter(news_category_id=2).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Entertainment']

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelEntertainmentChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=entertainment&lang=ch'

    def items(self):
        return News.objects.filter(news_category_id=2).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Entertainment']

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelEntertainmentRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=entertainment&lang=rus'

    def items(self):
        return News.objects.filter(news_category_id=2).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Entertainment']

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelEntertainmentWeekEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=entertainment&range=week&lang=eng'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=2).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Entertainment']

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelEntertainmentWeekChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=entertainment&range=week&lang=ch'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=2).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Entertainment']

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelEntertainmentWeekRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=entertainment&range=week&lang=rus'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=2).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Entertainment']

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelAutoEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=auto&lang=eng'

    def items(self):
        return News.objects.filter(news_category_id=3).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Auto']

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelAutoChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=auto&lang=ch'

    def items(self):
        return News.objects.filter(news_category_id=3).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Auto']

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelAutoRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=auto&lang=rus'

    def items(self):
        return News.objects.filter(news_category_id=3).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Auto']

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelAutoWeekEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=auto&range=week&lang=eng'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=3).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Auto']

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelAutoWeekChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=auto&range=week&lang=ch'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=3).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Auto']

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelAutoWeekRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=auto&range=week&lang=rus'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=3).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Auto']

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelSpaceEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=space&lang=eng'

    def items(self):
        return News.objects.filter(news_category_id=4).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Space']

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelSpaceChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=space&lang=ch'

    def items(self):
        return News.objects.filter(news_category_id=4).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Space']

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelSpaceRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=space&lang=rus'

    def items(self):
        return News.objects.filter(news_category_id=4).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Space']

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelSpaceWeekEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=space&range=week&lang=eng'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=4).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Space']

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelSpaceWeekChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=space&range=week&lang=ch'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=4).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Space']

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelSpaceWeekRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=space&range=week&lang=rus'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=4).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Space']

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelBioEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=bio&lang=eng'

    def items(self):
        return News.objects.filter(news_category_id=5).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['BIO']

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelBioChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=bio&lang=ch'

    def items(self):
        return News.objects.filter(news_category_id=5).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['BIO']

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelBioRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=bio&lang=rus'

    def items(self):
        return News.objects.filter(news_category_id=5).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['BIO']

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelBioWeekEnglish(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=bio&range=week&lang=eng'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=5).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['BIO']

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelBioWeekChinese(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=bio&range=week&lang=ch'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=5).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['BIO']

    def item_title(self, item):
        return item.news_title_chinese

    def item_description(self, item):
        return item.news_post_text_chinese

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"
class RssChannelBioWeekRussian(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=bio&range=week&lang=rus'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=5).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['BIO']

    def item_title(self, item):
        return item.news_title_russian

    def item_description(self, item):
        return item.news_post_text_russian

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelCompany(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=company&name='


    def get_object(self, request, company_name):
        name = company_name
        return Companies.objects.get(verbose_name=company_name)

    def items(self, item):
        return News.objects.filter(news_company_owner_id=item.id).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_title(self, item):
        return item.news_title_english

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


def get_current_company_rss(request):
    if request.POST:
        return HttpResponseRedirect('/rss/news&channel=company&name=%s' % request.POST['rss-company'])
