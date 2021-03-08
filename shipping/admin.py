from django.contrib import admin
from .models import Region, PostageRate, CountryRegion, PostageType

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):

	fields = (('region',))
	list_display = ('region',)
	ordering = ('region',)
	search_fields=('region',)
	list_filter=('region',)


@admin.register(CountryRegion)
class CountryRegionAdmin(admin.ModelAdmin):

	fields = (('country_code', 'region'))
	list_display = ('country_code','region')
	ordering = ('country_code','region',)
	search_fields=('country_code','region',)
	list_filter=('region',)


@admin.register(PostageRate)
class PostageRateAdmin(admin.ModelAdmin):

	fields = (('id'),
		('region'),
		('postage_type'),
		('postage_rate'),
		('postage_rate_max_items'),
		('postage_rate_per_extra_item'),
		('date_created'),
		('last_edited'))
	readonly_fields = ('id','date_created', 'last_edited',)
	list_display = ('id','region','postage_type', 'postage_rate','postage_rate_max_items','postage_rate_per_extra_item','date_created','last_edited',)
	ordering = ('region',)
	search_fields=('region','postage_type',)
	list_filter=('region',)

@admin.register(PostageType)
class PostageTypeAdmin(admin.ModelAdmin):

	fields = (('postage_id'),
		('postage_short_desc'))
	list_display = ('postage_id','postage_short_desc',)
	ordering = ('postage_id',)
