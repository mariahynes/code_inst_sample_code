from django import template
from django.conf import settings
from orders.models import Order, OrderItem
from products.models import Product
from django.db.models import Sum, Exists
from django.db import models
import products.templatetags.product_extras as product_extras
import carts.templatetags.cart_extras as cart_extras
import shop.templatetags.global_extras as global_extras
import shipping.templatetags.shipping_extras as shipping_extras
import discounts.templatetags.discount_extras as discount_extras
from django.core.mail import EmailMultiAlternatives
import datetime
from django.utils import timezone

register = template.Library()

def get_cart_id_from_order(order_id):

    cart_id = ""
    the_order = get_order(order_id)

    if the_order:

        cart_id = the_order.cart_ID

    return cart_id  

def get_cart_id_payment_status(cart_id):

    try:

        the_order = Order.objects.get(cart_ID=cart_id)

    except Order.DoesNotExist:

        payment_status = ""

    else:
        #there is a record with this Cart id
        payment_status = the_order.payment_status
        #print("payment_status from table")
        #print(payment_status)

    return payment_status

def get_cart_id_payment_method(cart_id):

    try:

        the_order = Order.objects.get(cart_ID=cart_id)

    except Order.DoesNotExist:

        payment_method = ""

    else:
        #there is a record with this Cart id
        payment_method = the_order.payment_method
        print("payment_method from table")
        print(payment_method)

    return payment_method
 
def get_payment_method_ref(order_id):

    the_order = get_order(order_id)

    if the_order:

        payment_method_ref = the_order.payment_ref_from_method

    else:

        payment_method_ref = ""

    return payment_method_ref


def create_order_from_cart(request, pay_method):
    
    #create a record in the Order table containing the cart_id
    #check that this cart_id isn't already in the table
    ok_to_create = True
    new_id = 0
    cart_id = cart_extras.get_cart_id(request) 
    cart_order_record = Order.objects.filter(cart_ID=cart_id)
   
    if (cart_order_record.exists()):
        #this should not be the norm so if this cart is already entered on an existing order this must mean that 
        #the customer is in the same session and is creating ANOTHER order.

        #check if the existing order has any payment_status (if it has ANY payment status, then need to stop order)
        the_payment_status = get_cart_id_payment_status(cart_id)
        
        if not the_payment_status or the_payment_status == "CANCELLED":
            #the original order does not have a payment status or is has a cancelled status so this new one CAN be recreated
            #deleting the order will also delete the products associated with the order
            print("this session id is already in the Order Table but in an unsuccessful Order")
            cart_order_record.delete()
            print("it is now deleted")

        else:
            #the original order has a payment status so it should not be over-written
            #UNLESS the user is using a DIFFERENT Payment Method (they may have changed their mind and selected the other option)
            #it CAN be overwritten if the payment type is different
            print("this session id is already in the Order Table and has a payment status")
            the_payment_method = get_cart_id_payment_method(cart_id)
            if the_payment_method == pay_method:
                print("Do not over write it")
                ok_to_create = False 
            else:
                print("this session id is already in the Order Table but in an unsuccessful Order AND a different payment method")
                cart_order_record.delete()
                print("it is now deleted")
                  

    if ok_to_create:  

        order_complete = False        
        cart_ID = cart_id
        order_discount_code = cart_extras.get_cart_discount_code(request)
        payment_method = pay_method
        shipping_name = cart_extras.get_shipping_address_name(request)
        shipping_address_line1 = cart_extras.get_shipping_address_line1(request)
        shipping_address_line2 = cart_extras.get_shipping_address_line2(request)
        shipping_address_city = cart_extras.get_shipping_address_city(request)
        shipping_address_state = cart_extras.get_shipping_address_state(request)
        shipping_address_postal_code = cart_extras.get_shipping_address_postal_code(request)
        shipping_address_country = cart_extras.get_shipping_address_country(request)
        customer_notes = cart_extras.get_customer_notes(request)

        shipping_type = cart_extras.get_postage_type(request)
        shipping_total = cart_extras.get_postage_cost(request)
        shipping_type_from_cart = shipping_extras.get_postage_type_display(shipping_type)
        shipping_total_from_cart = shipping_total
        discount_total = cart_extras.get_cart_discount_amount(request)
        order_discount_code = cart_extras.get_cart_discount_code(request)
        sub_total_from_cart = cart_extras.get_sub_total(request)
        final_total_from_cart = cart_extras.get_final_total(request)

        if pay_method == "FREE":
            payment_status = "FREE"
        else:
            payment_status = "PENDING"

        new_order = Order(cart_ID=cart_id, order_complete=order_complete, payment_method=payment_method, payment_status=payment_status,
            shipping_name = shipping_name, shipping_address_line1 = shipping_address_line1, shipping_address_line2 = shipping_address_line2,
            shipping_address_city = shipping_address_city, shipping_address_state =shipping_address_state, 
            shipping_address_postal_code = shipping_address_postal_code, shipping_address_country = shipping_address_country,
            customer_notes=customer_notes, shipping_type=shipping_type,shipping_total =shipping_total, 
            shipping_type_from_cart=shipping_type_from_cart, shipping_total_from_cart = shipping_total_from_cart, discount_total=discount_total,
            order_discount_code=order_discount_code,sub_total_from_cart =sub_total_from_cart,final_total_from_cart=final_total_from_cart )

        new_order.save()
        new_id = new_order.pk
        #print("The new ID is ")
        #print(new_id)
        if new_id:

            the_cart_items = cart_extras.get_cart_items_object(request)

            for item in the_cart_items:
                product_id = cart_extras.get_product_id(request, item)
                the_product = product_extras.get_product(product_id)
                product_quantity = cart_extras.get_product_quantity(request, item)
                product_price_for_order = product_extras.get_product_price(product_id)
                
                new_item = OrderItem(order_ID = new_order, product_ID = the_product, product_quantity = product_quantity, 
                    product_price_for_order = product_price_for_order)
                new_item.save()

            #check if this new_id (order_id) needs to be recorded in discount table
            #need to be only if a single-use discount code was used (so that it can't be reused)
            if order_discount_code:
                usage_frequency = discount_extras.get_usage_frequency(order_discount_code)
                #print(usage_frequency)
                if usage_frequency == "SINGLE_USE":
                    discount_extras.add_single_use_order_id(order_discount_code, get_order(new_id))

    return new_id

def get_order(order_id):

    the_order = {}

    try:

        the_order = Order.objects.get(id=order_id)

    except Order.DoesNotExist:

        the_order = {}

    return the_order

def get_order_items(order_id):

    the_order_items = {}
    the_order = get_order(order_id)

    if the_order:

        order_id = the_order.id

        try:

            the_order_items = OrderItem.objects.all().filter(order_ID=order_id)

        except OrderItem.DoesNotExist:

            the_order_items = {}

    return the_order_items


def format_order_items_for_stripe(order_id):
    
    #optional function - code uses the 'format_cart_items_for_stripe' instead as it's quicker, 
    #but this is an alternative (it's the same info)

    line_items = []

    order_products = get_order_items(order_id)

    for item in order_products:

        product_ID = item.product_ID
        product_name = product_extras.get_product_name(item.product_ID_id)
        product_quantity = item.product_quantity    
        product_price = item.product_price_for_order
        product_price_currency = product_extras.get_product_price_currency(item.product_ID_id)

        #format the price as an int for sending 
        product_price = int(product_price * 100)

        if product_extras.has_sirv_image(item.product_ID_id):
            item_image = product_extras.get_product_sirv_url(item.product_ID_id)
        else:
            item_image = product_extras.get_product_image_1(item.product_ID_id)
    
        line_item = {
            
            'price_data': {

                'unit_amount': product_price,
                'currency': product_price_currency,

                'product_data': {
                    'name': product_name,
                    'images': [item_image],
                    "metadata": {
                        'product_id': product_ID,
                    }
                },          

            },

            'quantity': product_quantity,

        }

        line_items.append(line_item)

    #add shipping line item
    #shipping details for line item
    
    the_order = get_order(order_id)
    postage_type_display = the_order.get_shipping_type_display()
    postage_cost = the_order.shipping_total

    #format the cost as an int for sending 
    postage_cost_int = int(postage_cost * 100)
    postage_currency = "EUR"

    shipping_logo = global_extras.get_logo_sirv_url()

    shipping_item = {
            
        'price_data': {

            'unit_amount': postage_cost_int,
            'currency': postage_currency,

            'product_data': {
                'name': "Shipping Cost",
                'description': postage_type_display,
                'images':[shipping_logo],
            },          

        },

        'quantity': 1,

    }

    line_items.append(shipping_item)

    return line_items   

@register.simple_tag
def get_total_product_items_available(product_id):

    the_product = product_extras.get_product(product_id)
    
    if the_product:

        product_name = product_extras.get_product_name(product_id)
        #print("total_available of " + product_name + ":")
        #available is total_manufactured less number of items sold
        total_manufactured = product_extras.get_product_stock_manufactured(product_id)  
        total_sold = get_product_units_sold(product_id)

        if total_manufactured > 0:
            total_available = total_manufactured - total_sold

    else:

        total_available = 0
    #print(total_available)      
    return total_available

def update_order_after_payment_cancel(order_id):

    order_updated = False
    the_order = get_order(order_id)

    if the_order:

        the_order.payment_status = "CANCELLED"
        the_order.save(update_fields=['payment_status'])
        order_updated = True

    return order_updated

def update_order_after_payment_fail(order_id):

    order_updated = False
    the_order = get_order(order_id)

    if the_order:

        the_order.payment_status = "FAILED"
        the_order.save(update_fields=['payment_status'])
        order_updated = True

    return order_updated

def update_order_after_payment_refund(order_id,refund_amount,refund_ref, refund_time_date_obj):

    order_updated = False
    the_order = get_order(order_id)

    if the_order:

        #reset 'order_complete' to False so that it is not included in inventory
        the_order.order_complete = False 
        the_order.order_refunded = True 
        the_order.payment_status = "REFUNDED"
        the_order.payment_refunded_amount = refund_amount
        the_order.payment_refunded_date = refund_time_date_obj
        the_order.payment_ref_from_refund = refund_ref
        
        the_order.save(update_fields=['order_complete','order_refunded','payment_status','payment_refunded_amount','payment_refunded_date','payment_ref_from_refund'])
        
        order_updated = True
        print("%s %s" %("Refunded completed for order: ", order_id))

    else:
        print("%s %s" %("Refund completed, but didn't get updated to Order table for some reason: ",order_id))

    return order_updated


def update_order_after_successful_payment(order_id,payment_amount,payment_ref, payment_time_date_obj):

    order_updated = False

    the_order = get_order(order_id)

    if the_order:
        the_order.order_complete = True
        the_order.payment_status = "PAID"
        the_order.payment_succeeded_amount = payment_amount
        the_order.payment_succeeded_date = payment_time_date_obj
        the_order.payment_ref_from_method = payment_ref

        the_order.save(update_fields=['order_complete','payment_status','payment_succeeded_amount','payment_succeeded_date','payment_ref_from_method'])
     
        order_updated = True
        #print("Checkout session completed")

    else:
        print("%s %s" %("Checkout session completed, but didn't get updated to Order table for some reason: ",order_id))

    return order_updated

def update_order_to_complete(order_id):

    order_updated = False

    the_order = get_order(order_id)

    if the_order:
        the_order.order_complete = True

        the_order.save(update_fields=['order_complete'])
     
        order_updated = True

    else:
        print("Order %s marked as completed, but Order table didn't get updated for some reason" %(order_id))

    return order_updated

def update_order_billing_email(order_id, customer_email):

    the_order = get_order(order_id)
    
    if the_order:
        the_order.billing_email = customer_email
        the_order.save(update_fields=['billing_email'])

        order_updated = True

    else:

        order_updated = False

    return order_updated

def update_order_billing_name(order_id, customer_name):

    the_order = get_order(order_id)
    
    if the_order:
        the_order.billing_name = customer_name
        the_order.save(update_fields=['billing_name'])

        order_updated = True

    else:

        order_updated = False

    return order_updated

def update_order_billing_paypal_payer_id(order_id, payer_id):

    the_order = get_order(order_id)
    
    if the_order:
        the_order.billing_paypal_payer_id = payer_id
        the_order.save(update_fields=['billing_paypal_payer_id'])

        order_updated = True

    else:

        order_updated = False

    return order_updated

def update_order_billing_paypal_payer_country_code(order_id, country_code):

    the_order = get_order(order_id)
    
    if the_order:
        
        the_order.billing_address_country = country_code
        the_order.save(update_fields=['billing_address_country'])

        order_updated = True

    else:

        order_updated = False

    return order_updated




def update_order_billing_details_STRIPE(stripe_obj):
    
    #the billing details are not available from Paypal API so this is just a step for STRIPE payments

    #order ID can be found in the metadata of the charges section of the Stripe Object
    #this is primary key of the order in the database
    order_id = stripe_obj.metadata.order_id
    
    #get the billing details from the stripe object to successfully update the Order table
    billing_address_city = stripe_obj.billing_details.address.city
    billing_address_country = stripe_obj.billing_details.address.country
    billing_address_line1 = stripe_obj.billing_details.address.line1
    billing_address_line2 = stripe_obj.billing_details.address.line2
    billing_address_postal_code = stripe_obj.billing_details.address.postal_code
    billing_address_state = stripe_obj.billing_details.address.state
    billing_email = stripe_obj.billing_details.email
    billing_name = stripe_obj.billing_details.name
    billing_phone = stripe_obj.billing_details.phone

    the_order = get_order(order_id)

    if the_order:

        the_order.billing_name = billing_name
        the_order.billing_address_line1 = billing_address_line1
        the_order.billing_address_line2 = billing_address_line2
        the_order.billing_address_city = billing_address_city
        the_order.billing_address_state = billing_address_state
        the_order.billing_address_postal_code = billing_address_postal_code
        the_order.billing_address_country = billing_address_country
        the_order.billing_email = billing_email
        the_order.billing_phone = billing_phone

        the_order.save(update_fields=['billing_name','billing_email','billing_phone',
            'billing_address_line1','billing_address_line2','billing_address_city',
            'billing_address_state','billing_address_postal_code','billing_address_country'])

        order_updated = True

    else:

        order_updated = False

    return order_updated

def update_order_confirmation_sent_to_shop(order_id, it_was_sent):

    was_updated = False
    the_order = get_order(order_id)

    if the_order:

        the_order.order_confirmation_sent_to_shop = it_was_sent
        the_order.date_order_confirmation_sent_to_shop= timezone.now()

        the_order.save(update_fields=['order_confirmation_sent_to_shop','date_order_confirmation_sent_to_shop'])

        was_updated = True

    else:
        was_updated = False
        print("%s %s" %("order id did not exist - shop email not sent ", order_id))

    return was_updated

def update_payment_fail_sent_to_shop(order_id, it_was_sent):

    was_updated = False
    the_order = get_order(order_id)

    if the_order:

        the_order.payment_failed_sent_to_shop = it_was_sent
        the_order.date_payment_failed_sent_to_shop= timezone.now()

        the_order.save(update_fields=['payment_failed_sent_to_shop','date_payment_failed_sent_to_shop'])

        was_updated = True

    else:
        was_updated = False
        print("%s %s" %("order id did not exist - payment fail email not sent to shop ", order_id))

    return was_updated

def update_payment_refund_sent_to_shop(order_id, it_was_sent):

    was_updated = False
    the_order = get_order(order_id)

    if the_order:

        the_order.payment_refund_sent_to_shop = it_was_sent
        the_order.date_payment_refund_sent_to_shop= timezone.now()

        the_order.save(update_fields=['payment_refund_sent_to_shop','date_payment_refund_sent_to_shop'])

        was_updated = True

    else:
        was_updated = False
        print("%s %s" %("order id did not exist - payment refund email not sent to shop ", order_id))

    return was_updated

def update_payment_refund_sent_to_customer(order_id, it_was_sent):

    was_updated = False
    the_order = get_order(order_id)

    if the_order:

        the_order.payment_refund_sent_to_customer = it_was_sent
        the_order.date_payment_refund_sent_to_customer = timezone.now()

        the_order.save(update_fields=['payment_refund_sent_to_customer','date_payment_refund_sent_to_customer'])

        was_updated = True

    else:
        was_updated = False
        print("%s %s" %("order id did not exist - payment refund email not sent to customer ", order_id))

    return was_updated

def update_order_confirmation_sent_to_customer(order_id, it_was_sent):

    was_updated = False
    the_order = get_order(order_id)

    if the_order:

        the_order.order_confirmation_sent_to_customer = it_was_sent
        the_order.date_order_confirmation_sent_to_customer = timezone.now()

        the_order.save(update_fields=['order_confirmation_sent_to_customer','date_order_confirmation_sent_to_customer'])

        was_updated = True

    else:
        was_updated = False
        print("%s %s" %("order id did not exist - customer email not sent", order_id))

    return was_updated

def update_payment_fail_sent_to_customer(order_id, it_was_sent):

    was_updated = False
    the_order = get_order(order_id)

    if the_order:

        the_order.payment_failed_sent_to_customer = it_was_sent
        the_order.date_payment_failed_sent_to_customer = timezone.now()

        the_order.save(update_fields=['payment_failed_sent_to_customer','date_payment_failed_sent_to_customer'])

        was_updated = True

    else:
        was_updated = False
        print("%s %s" %("order id did not exist - payment fail email not sent to customer", order_id))

    return was_updated

def prepare_order_email(order_id, type, status=""):
    #type can be 'shop' or 'customer'
    #status is blank by default, but can be 'FAILED', 'FREE' or 'REFUNDED'

    email_template = ""
    email_sent = False
    the_order = get_order(order_id)
   
    if the_order:

        order_items = get_order_items(order_id)
        
        # prepare PRODUCT DETAILS FOR THE EMAIL
        if type == "shop":
            product_details = "<tr><th>Item</th><th style='text-align:center;'>Qty</th><th style='text-align:center;'>Price</th><th style='text-align:center;'>Item Subtotal</th><th style='text-align:center;'>(Stock Remaining)</th></tr>"
        elif type == "customer":
            product_details = "<tr><th>Item</th><th style='text-align:center;'>Qty</th><th style='text-align:center;'>Price</th><th style='text-align:center;'>Item Subtotal</th></tr>"

        for item in order_items:
            product_name = product_extras.get_product_name(item.product_ID.id)
            product_quantity = item.product_quantity
            product_price = item.product_price_for_order
            product_sub_total = item.product_subtotal()

            if type == "shop":
                remaining_stock = get_total_product_items_available(item.product_ID.id)
                remaining_stock_text = "%s %s" %("Remaining Stock: ", remaining_stock)
                product_details = product_details + "<tr><td>%s</td><td style='text-align:center;'>%s</td><td style='text-align:center;'>%s</td><td style='text-align:center;'>%s</td><td style='text-align:center;'>%s</td></tr>" %(product_name, product_quantity, product_price,product_sub_total, remaining_stock)

            elif type == "customer":
                product_details = product_details + "<tr><td>%s</td><td style='text-align:center;'>%s</td><td style='text-align:center;'>%s</td><td style='text-align:center;'>%s</td></tr>" %(product_name, product_quantity,product_price,product_sub_total)
        
        # prepare EMAIL DETAILS and SEND EMAIL
        if type == "shop":

            if status=="FAILED":
                email_template = "orders/payment_fail_notification_to_shop_email.html"
                the_subject = "%s: Failed Order #%s" %(settings.SITE_DISPLAY_NAME, order_id)
            
            elif status=="FREE":
                email_template = "orders/free_order_notification_to_shop_email.html"
                the_subject = "%s: Free Order #%s" %(settings.SITE_DISPLAY_NAME, order_id)

            elif status=="REFUNDED":
                email_template = "orders/refunded_order_notification_to_shop_email.html"
                the_subject = "%s: Refunded Order #%s" %(settings.SITE_DISPLAY_NAME, order_id)

            else:
                email_template = "orders/notification_to_shop_email.html"
                the_subject = "%s: New Order #%s" %(settings.SITE_DISPLAY_NAME, order_id)

            to_email = settings.EMAIL_HOST_USER
            payment_method_link = the_order.order_payment_method_link()
            payment_ref_from_payment_method = the_order.payment_ref_from_method
            cart_id = the_order.cart_ID
            order_link = the_order.link_to_order()
            order_discount_code = the_order.order_discount_code
            if order_discount_code:
                order_discount_desc = discount_extras.get_discount_description(order_discount_code)
            else:
                order_discount_desc = ""

        elif type == "customer":
            if status=="FAILED":
                email_template = "orders/payment_fail_notification_to_customer_email.html"
                the_subject = "%s %s" %(settings.SITE_DISPLAY_NAME, " Order Declined")
            elif status=="FREE":
                #FYI customer doesn't get an email if the order is FREE (only shop owner does)
                email_template = "orders/free_order_notification_to_customer_email.html"
                the_subject = "%s: Your Order #%s" %(settings.SITE_DISPLAY_NAME, order_id)
            elif status=="REFUNDED":
                email_template = "orders/refunded_order_notification_to_customer_email.html"
                the_subject = "%s: Refunded Order #%s" %(settings.SITE_DISPLAY_NAME, order_id)
            else:
                email_template = "orders/notification_to_customer_email.html"
                the_subject = "%s %s" %(settings.SITE_DISPLAY_NAME, " Order Confirmation")

            to_email = the_order.billing_email
            payment_method_link = ""
            payment_ref_from_payment_method = the_order.payment_ref_from_method 
            cart_id = "" 
            order_link = ""  
            order_discount_code = "" #don't send again, don't remind them of it!
            order_discount_desc = ""

        if the_order.payment_method == "STRIPE":
            if type == "customer":
                payment_method = "Credit Card"
            else:
                payment_method = "Credit Card (STRIPE)"
        else:
            payment_method = the_order.payment_method

        if email_template:

            the_html_email = global_extras.prepare_template_as_string({"product_details":product_details,
                "site_name": global_extras.return_site_name(),
                "shipping_type":the_order.get_shipping_type_display(), 
                "shipping_cost":the_order.shipping_total, 
                "payment_method": payment_method,
                "sub_total": the_order.order_subtotal_amount,
                "order_discount_amount":the_order.discount_total,
                "order_discount_code":order_discount_code,
                "order_discount_desc":order_discount_desc,
                "total": the_order.order_total_amount,
                "payment_method_link": payment_method_link,
                "payment_ref_from_payment_method":payment_ref_from_payment_method,
                "refund_total": the_order.payment_refunded_amount,
                "payment_ref_from_refund":the_order.payment_ref_from_refund,
                "order_id": order_id,
                "cart_id": cart_id,
                "order_link": order_link,
                "billing_email": the_order.billing_email,
                "billing_address": format_address_lined(the_order, "billing"),
                "shipping_address": format_address_lined(the_order, "shipping"),
                "customer_notes": the_order.customer_notes}, email_template)
   
        the_text_email = the_html_email #just make it all html for now
        from_email = settings.DEFAULT_FROM_EMAIL

        msg = EmailMultiAlternatives(the_subject, the_text_email, from_email, [to_email], reply_to=[from_email])
        msg.attach_alternative(the_html_email, "text/html")
        
        try:
            msg.send(fail_silently=False)
            email_sent = True

        except Exception as e:
            print("%s %s %s %s %s" %("email not sent for order ", order_id, " with payment ref ", payment_ref_from_payment_method, str(e)))
            email_sent = False

        

        # update the ORDER RECORD EMAIL CONFIRMATION fields
        if type == "shop":
            #status is blank by default (which is a normal new order confirmation), but can be 'FAILED', 'FREE' or 'REFUNDED'
            if status == "FAILED":
                update_payment_fail_sent_to_shop(order_id, email_sent)
            elif status == "FREE":
                #same as new order email
                update_order_confirmation_sent_to_shop(order_id, email_sent)
            elif status == "REFUNDED":
                update_payment_refund_sent_to_shop(order_id, email_sent)
            else:
                #update the Order table to say, email has been sent to shop owner
                update_order_confirmation_sent_to_shop(order_id, email_sent)

        elif type == "customer":
            #status is blank by default, but can be 'FAILED', 'FREE' or 'REFUNDED'
            if status == "FAILED":
                update_payment_fail_sent_to_customer(order_id, email_sent)
            elif status == "FREE":
                #no free email sent to customer (as shop needs to see first to see if it's valid)
                pass
            elif status == "REFUNDED":
                update_payment_refund_sent_to_customer(order_id, email_sent)
            else:
                update_order_confirmation_sent_to_customer(order_id, email_sent)

        #print(the_html_email)

    else:
        email_sent = False
        print("%s %s" %("order id did not exist - email not sent", order_id))

    return email_sent

def format_address_lined(the_order, type):

    #type can be billing or shipping
    #the_order is the full order object (not just the order_id)
    if type=="billing":

        the_address = global_extras.prepare_template_as_string({"name":the_order.billing_name,
            "address_1":the_order.billing_address_line1, 
            "address_2":the_order.billing_address_line2, 
            "city": the_order.billing_address_city, 
            "state":the_order.billing_address_state, 
            "postal_code": the_order.billing_address_postal_code, 
            "country": the_order.billing_address_country.name,
            "country_code":the_order.billing_address_country}, "orders/address_format.html")

    elif type =="shipping":

        the_address = global_extras.prepare_template_as_string({"name":the_order.shipping_name,
            "address_1":the_order.shipping_address_line1, 
            "address_2":the_order.shipping_address_line2, 
            "city": the_order.shipping_address_city, 
            "state":the_order.shipping_address_state, 
            "postal_code": the_order.shipping_address_postal_code, 
            "country": the_order.shipping_address_country.name,
            "country_code":the_order.shipping_address_country},"orders/address_format.html")

    else:
        the_address = ""
  
    return the_address

def get_successful_orders():

    the_orders = {}
    the_orders = Order.objects.all().filter(order_complete=True)

    return the_orders

def get_total_units_sold():

    sum_of_success = 0
    #check the order table for successful orders
    #sum up the quantities of these orders
    the_success_orders = get_successful_orders()

    for order in the_success_orders:
        sum_of_success = sum_of_success + order.order_quantity()

    return sum_of_success
    

def get_product_units_sold(product_id):

    the_product_quantity = 0
    the_orders = {}
    all_orders = get_successful_orders()

    for order in all_orders:
   
        the_order_details = OrderItem.objects.all().filter(order_ID = order, product_ID_id = product_id)

        for record in the_order_details:
            the_product_quantity = the_product_quantity + record.product_quantity

    return the_product_quantity


