from django import template
from django.conf import settings
from discounts.models import Discount
from django.db import models
import products.templatetags.product_extras as product_extras
import datetime
from django.utils import timezone

register = template.Library()

@register.simple_tag
def get_discount_record(discount_code):

    try:
        the_discount_record = Discount.objects.get(discount_code=discount_code)

    except Discount.DoesNotExist:

        the_discount_record = {}

    else:

        return the_discount_record

@register.simple_tag
def get_discount_record_with_order_id(order_obj):

    try:
        the_discount_record = Discount.objects.get(used_by_order_id=order_obj)

    except Discount.DoesNotExist:

        the_discount_record = {}

    else:

        return the_discount_record

@register.simple_tag
def is_active(discount_code):

    the_discount_record = get_discount_record(discount_code)
    is_active = False

    if the_discount_record:

        is_active = the_discount_record.is_active()

    return is_active

@register.simple_tag
def is_expired(discount_code):

    the_discount_record = get_discount_record(discount_code)
    is_expired = False

    if the_discount_record:

        is_expired = the_discount_record.is_expired()

    return is_expired

@register.simple_tag
def is_available(discount_code):

    the_discount_record = get_discount_record(discount_code)
    is_available = False

    if the_discount_record:

        is_available = the_discount_record.is_available()

    return is_available

def get_discount_percentage(discount_code):

    the_discount_record = get_discount_record(discount_code)
    discount_percentage = 0

    if the_discount_record:

        discount_percentage = the_discount_record.discount_percentage

    return discount_percentage

@register.simple_tag
def get_discount_description(discount_code):

    the_discount_record = get_discount_record(discount_code)
    discount_desc = ""

    if the_discount_record:

        discount_desc = the_discount_record.discount_desc()

    return discount_desc

def get_usage_frequency(discount_code):

    the_discount_record = get_discount_record(discount_code)
    usage_frequency = 0

    if the_discount_record:

        usage_frequency = the_discount_record.usage_frequency

    return usage_frequency

def get_discount_type(discount_code):

    the_discount_record = get_discount_record(discount_code)
    discount_type = 0

    if the_discount_record:

        discount_type = the_discount_record.discount_type

    return discount_type

def get_discount_product_id(discount_code):

    the_discount_record = get_discount_record(discount_code)
    discount_product_id = 0

    if the_discount_record:

        discount_product_id = the_discount_record.product_id_id

    return discount_product_id


def calculate_discount_amount(the_discount_percentage, the_amount_before_discount):

    #the_amount_before_discount comes from the cart could be a string or decimal
    #convert to float

    the_discount_amount = "0.00"
  
    the_amount_float = float(the_amount_before_discount)
    
    if the_amount_float > 0:
       
        if the_discount_percentage > 0:
            
            the_discount_amount = the_amount_float * float(the_discount_percentage)
    
    return the_discount_amount


def get_discount_amount_and_message(sCode, discount_type, shipping_total, product_totals_obj, final_total):
    
    #check if this discount code provided by the customer is available
    code_is_available = is_available(sCode)

    if code_is_available:
        
        discount_percentage = get_discount_percentage(sCode)
        discount_type = get_discount_type(sCode)
        discount_desc = get_discount_description(sCode)
        discount_code = sCode

        #depending on the type of discount (SHIPPING, PRODUCT OR ORDER)
        #get the amount before reduction

        if discount_type == "PRODUCT":
            #which product can get the discount?
            discount_product_id = get_discount_product_id(sCode)
            #check if this product_id is in the product_totals dict provided
            if discount_product_id in product_totals_obj:
                amount_before_discount = product_totals_obj[discount_product_id]
            else:
                amount_before_discount = "0.00"

        elif discount_type == "SHIPPING":
            amount_before_discount = shipping_total
            
        elif discount_type == "ORDER":
            amount_before_discount = final_total
        
        discount_amount = calculate_discount_amount(discount_percentage, amount_before_discount)
    
        if discount_amount != "0.00":
           
            discount_amount = "{:.2f}".format(discount_amount)
            discount_message = "Discount of %s applied." %(discount_amount)
        else:
            discount_message = "Discount code approved."

    else:
        
        #code is unavailable (i.e. could be invalid or it could be expired)
        #set to no code and no discount
        discount_amount = "0.00"
        discount_code = ""
        discount_message = "Sorry, this code is invalid. No discount applied."
        discount_desc = "No discount applied"

    return discount_amount, discount_code, discount_message, discount_desc

def add_single_use_order_id(the_code, the_order_obj):

    the_discount_record = get_discount_record(the_code)
    was_updated = False

    if the_discount_record:

        the_discount_record.used_by_order_id = the_order_obj

        the_discount_record.save(update_fields=['used_by_order_id'])

        was_updated = True

    else:
        was_updated = False
        print("Single Use discount code %s used by order id %s, but discount table record not updated" %(the_code, the_order_obj))

    return was_updated
 
def remove_single_use_order_id(the_order_obj):

    the_discount_record = get_discount_record_with_order_id(the_order_obj)

    if the_discount_record:

        the_discount_record.used_by_order_id = None
        the_discount_record.save(update_fields=['used_by_order_id'])
        was_updated = True