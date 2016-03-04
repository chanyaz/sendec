from django.contrib import admin
from advert.models import Advertisement, AdvertClicks, AdvertViews, AdvertCTR, AdvertBudget


class AdvertisementAdmin(admin.ModelAdmin):
    model = Advertisement
    list_display = ['owner', 'name', 'data']
    list_filter = ['owner', 'name', 'data']


class AdvertClicksAdmin(admin.ModelAdmin):
    model = AdvertClicks
    list_display = ['advert', 'clicks']
    list_filter = ['advert', 'clicks']


class AdvertViewsAdmin(admin.ModelAdmin):
    model = AdvertViews
    list_display = ['advert', 'views']
    list_filter = ['advert', 'views']


class AdvertCTRAdmin(admin.ModelAdmin):
    model = AdvertCTR
    list_display = ['advert', 'ctr']
    list_filter = ['advert', 'ctr']


class AdvertBudgetAdmin(admin.ModelAdmin):
    model = AdvertBudget
    list_display = ['advert', 'budget']
    list_filter = ['advert', 'budget']

admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(AdvertClicks, AdvertClicksAdmin)
admin.site.register(AdvertViews, AdvertViewsAdmin)
admin.site.register(AdvertCTR, AdvertCTRAdmin)
admin.site.register(AdvertBudget, AdvertBudgetAdmin)