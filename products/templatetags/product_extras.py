from django import template
from django.conf import settings
from products.models import Product

register = template.Library()

@register.simple_tag
def get_active_products():

    the_products = Product.objects.all().filter(is_activated=True)

    return the_products

@register.simple_tag
def get_product(product_id):

    try:
        the_product = Product.objects.get(id=product_id)

    except Product.DoesNotExist:

        the_product = {}

    else:

        return the_product


@register.simple_tag
def get_product_name(product_id):

    the_product = get_product(product_id)

    if the_product:

        product_name = the_product.product_display_name

    else:

        product_name = ""

    return product_name

@register.simple_tag
def get_product_description(product_id):

    the_product = get_product(product_id)

    if the_product:

        product_desc = the_product.product_description

    else:

        product_desc = ""

    return product_desc

@register.simple_tag
def get_product_price(product_id):

    the_product = get_product(product_id)

    if the_product:
        product_price = the_product.product_price

    else:
        product_price = 0

    return product_price

@register.simple_tag
def get_product_price_currency(product_id):

    the_product = get_product(product_id)

    if the_product:
        product_price_currency = the_product.product_price_currency

    else:
        product_price_currency = ""

    return product_price_currency

@register.simple_tag
def get_max_per_purchase(product_id):
    
    the_product = get_product(product_id)

    if the_product:
        max_allowed = the_product.max_per_cart

    else:
        max_allowed = 0

    return max_allowed

@register.simple_tag
def has_sirv_image(product_id):

    the_product = get_product(product_id)

    if the_product:

        if the_product.product_image_sirv_1:
            has_sirv_image = True
        else:
            has_sirv_image = False

    else:

        has_sirv_image = False

    return has_sirv_image

@register.simple_tag
def get_product_sirv_url(product_id):

    the_product = get_product(product_id)

    if the_product:

        sirv_url = the_product.product_image_sirv_1

    else:

        sirv_url = ""

    return sirv_url

@register.simple_tag
def get_product_image_url(product_id):

    #this gets sirv first, if available, and then image_1 if not
    image_url = ""
    the_product = get_product(product_id)

    if the_product:

        if get_product_sirv_url(product_id):

            image_url = the_product.product_image_sirv_5

        else:
            
            image_1_url = the_product.product_image_1
            image_url = settings.MEDIA_URL + str(image_1_url)

    else:

        image_url = ""
        
       
    return image_url

def get_product_image_1(product_id):

    the_product = get_product(product_id)

    if the_product:

        image_1_url = the_product.product_image_1
        
        if image_1_url:
            #add media prefix
            image_1_url = settings.MEDIA_URL + str(image_1_url)

    else:

        image_1_url = ""

    return image_1_url


@register.simple_tag
def get_product_stock_manufactured(product_id):

    the_product = get_product(product_id)

    if the_product:
        stock = the_product.stock_manufactured

    else:
        stock = 0

    return stock

def get_product_images_and_desc(product_id):

    images_and_desc = {}
    the_product = get_product(product_id)

    if the_product:
        if the_product.product_image_1:
            images_and_desc[the_product.product_image_1] = the_product.product_image_1_desc
        if the_product.product_image_2:
            images_and_desc[the_product.product_image_2] = the_product.product_image_2_desc
        if the_product.product_image_3:
            images_and_desc[the_product.product_image_3] = the_product.product_image_3_desc
        if the_product.product_image_4:
            images_and_desc[the_product.product_image_4] = the_product.product_image_4_desc

    else:

        images_and_desc = {}
        
    return images_and_desc




