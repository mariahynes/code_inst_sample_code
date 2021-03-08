from django import template
from django_countries import countries
from shipping.models import Region, CountryRegion, PostageRate, PostageType

register = template.Library()

@register.simple_tag
def get_country_name(country_code):

	if country_code:
		country_name = dict(countries)[country_code]
	else:
		country_name = ""
	
	return country_name

@register.simple_tag
def get_shipping_cost(country_code, num_items, postageType):
    #returns one cost
    the_cost = 0

    if country_code:

        the_region = get_region(country_code)
        the_rate_obj = get_postage_rate_obj(the_region, postageType)

        if the_rate_obj:

            the_rate = the_rate_obj.postage_rate
            max_items = the_rate_obj.postage_rate_max_items
            per_extra_item = the_rate_obj.postage_rate_per_extra_item
            
            if num_items <= max_items:
                #no per_extra_item needed
                the_cost = the_rate

            else:
                #more than max is ordered so for each additional item, add on the per_extra_item cost
                additional_items = num_items - max_items
                the_cost = the_rate + (per_extra_item * additional_items)

    return the_cost


@register.simple_tag
def get_region(country_code):

    #if the country code is not in the CountryRegion Table
    #it is considered to be 'The Rest of the World' Category (code = 'Z')

    the_code = ""

    try:
        
        the_region = CountryRegion.objects.get(country_code=country_code)
        the_code = the_region.region_id

    except CountryRegion.DoesNotExist:

        the_code = "Z"

    return the_code

@register.simple_tag
def get_postage_rate_obj(region, postageType):
    
    try:
        
        the_rate_obj = PostageRate.objects.all().filter(region=region, postage_type=postageType).order_by('-last_edited')[0]

    except PostageRate.DoesNotExist:

        the_rate_obj = {}

    return the_rate_obj 


@register.simple_tag
def get_postage_type_display(postageType):

    the_display_name = ""
    the_choices = PostageRate._meta.get_field('postage_type').choices
    
    for item in the_choices:
        
        if item[0] == postageType:
            the_display_name = item[1]

    
    return the_display_name

@register.simple_tag
def get_postage_type_description(postageType):

    try:

        the_record = PostageType.objects.get(postage_id=postageType)
        the_description = the_record.postage_short_desc
        
    except PostageType.DoesNotExist:

        the_description = ""

    return the_description

