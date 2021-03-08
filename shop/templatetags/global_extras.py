from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django_countries import countries

register = template.Library()

@register.simple_tag
def return_site_name():

    site_name = settings.SITE_DISPLAY_NAME

    return site_name

@register.simple_tag
def return_ga_setting():
	#should return 'test' or 'live'
    ga_setting = settings.GOOGLE_ANALYTICS_MODE

    return ga_setting

@register.simple_tag
def return_paypal_mode():
	#should return 'sandbox' or 'live'
    paypal_mode = settings.PAYPAL_MODE

    return paypal_mode

@register.simple_tag
def return_stripe_mode():
	#should return 'test' or 'live'
    stripe_mode = settings.STRIPE_MODE

    return stripe_mode

@register.simple_tag
def return_domain_url():
    #should return 'test' or 'live'
    domain_url = settings.DOMAIN_URL

    return domain_url

@register.simple_tag
def return_paypal_client():
    #should return 'test' or 'live'
    paypal_client_id = settings.PAYPAL_CLIENT_ID

    return paypal_client_id

@register.simple_tag
def return_facebook_id():
  
    facebook_id = settings.FACEBOOK_KEY

    return facebook_id

@register.simple_tag
def return_facebook_pixel_id():
   
    facebook_pixel_id = settings.FACEBOOK_PIXEL_ID

    return facebook_pixel_id

@register.simple_tag
def return_domain_url_no_slash():
    #should return 'test' or 'live'
    domain_url = settings.DOMAIN_URL
    domain_url = domain_url[0:-1]
    return domain_url

def prepare_template_as_string(dict_values, template_location):

    return render_to_string(template_location, dict_values)

@register.simple_tag
def zero_in_cart():

	return 0;


@register.simple_tag
def get_logo_sirv_url():

	sirv_url = "https://databasis.sirv.com/Images/shadydog/shady_dog_product_images/shady_dog_logo.jpg"
       
	return sirv_url