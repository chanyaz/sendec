from django.shortcuts import render
from news.models import News
from django.contrib.auth.models import User, auth
from django.views.generic import TemplateView
from django.contrib.syndication.views import Feed
from django.template.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.core.urlresolvers import reverse
from news.models import NewsCategory, Companies
import datetime


class RenderRSSPage(TemplateView):

    template_name = "rss.html"

    def get_context_data(self, **kwargs):
        context = super(RenderRSSPage, self).get_context_data()
        context['username'] = self.request.user
        context['title'] = "RSS | "
        context['latest_news'] = self.get_news_offset(offset=6)
        context['footer_news'] = self.get_news_offset(offset=3)
        return context

    def get_news_offset(self, offset):
        return News.objects.order_by("-news_post_date")[:offset].values()


class RssChannelLatest(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=latest'

    def items(self):
        return News.objects.filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelLatestWeek(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=latest&range=week'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return ["Evgeny Privalov"]

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelTechnology(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=technology'

    def title(self):
        return "Technology news"

    def items(self):
        return News.objects.filter(news_category_id=1).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Technology']

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelTechnologyWeek(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=technology&range=week'

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
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelEntertainment(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=entertainment'

    def items(self):
        return News.objects.filter(news_category_id=2).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Entertainment']

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelEntertainmentWeek(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=entertainment&range=week'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=2).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Entertainment']

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelAuto(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=auto'

    def items(self):
        return News.objects.filter(news_category_id=3).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Auto']

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelAutoWeek(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=auto&range=week'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=3).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Auto']

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelSpace(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=space'

    def items(self):
        return News.objects.filter(news_category_id=4).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Space']

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelSpaceWeek(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=space&range=week'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=4).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['Space']

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelBio(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=bio'

    def items(self):
        return News.objects.filter(news_category_id=5).filter(news_post_date__hour='00').order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['BIO']

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


class RssChannelBioWeek(Feed):

    title_template = "Rss Channel of Insydia"
    description_template = "desc"
    link = '/rss/news&channel=bio&range=week'

    def items(self):
        current_day = datetime.datetime.now() - datetime.timedelta(days=7)
        return News.objects.filter(news_category_id=5).filter(news_post_date__gt=current_day).order_by("-news_post_date")[:10]

    def item_pubdate(self, item):
        return item.news_post_date

    def item_categories(self, item):
        return ['BIO']

    def item_title(self, item):
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

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
        return item.news_title

    def item_description(self, item):
        return item.news_post_text_english

    def author_name(self):
        return "Evgeny Privalov"

    def author_email(self):
        return "eprivalov@insydia.com"


def get_current_company_rss(request):
    if request.POST:
        return HttpResponseRedirect('/rss/news&channel=company&name=%s' % request.POST['rss-company'])
