from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse
import products.templatetags.product_extras as product_extras
import orders.templatetags.order_extras as order_extras
import shop.templatetags.global_extras as global_extras
import discounts.templatetags.discount_extras as discount_extras
import carts.templatetags.cart_extras as cart_extras
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import stripe

def index(request):
	
	request.session.set_test_cookie()

	active_products = {}
	
	active_products = product_extras.get_active_products()
	
	if active_products:

		for item in active_products:
			
			product_id = item.id
			available_stock = order_extras.get_total_product_items_available(product_id)

		#is there a cart?
		#check if cart already exists for this session
		if request.COOKIES:
			if 'cart_id' in request.session:
				#use this for adding to a View Cart button (with badge)
				cart_id = request.session['cart_id']
			else:
				cart_id = ""
			
		else:
			#no cookies but tell the user later (only need it if they are adding something to the cart) 
			cart_id = ""
					

	return render(request, 'shop/shop.html', {"active_products": active_products,"cart_id":cart_id})


@csrf_exempt
def facebook_config(request):

	if request.method == 'GET':
		facebook_id = settings.FACEBOOK_KEY
		facebook_token = settings.FACEBOOK_TOKEN
		#access_token = "%s|%s" %(facebook_id,facebook_token)
		access_string = "client_id=%s&client_secret=%s" %(facebook_id,facebook_token)
		facebook_config = {'access_token': access_string}
		return JsonResponse(facebook_config, safe=False)


@csrf_exempt
def stripe_config(request):

	if request.method == 'GET':
		stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
		return JsonResponse(stripe_config, safe=False)





def payment_checks(request, order_id, order_cart_id):

	payment_status = ""
	#check that's it is a real order_ref (i.e. order_id)
	cart_id = order_extras.get_cart_id_from_order(order_id)

	#check if the cart_id in the order matches the cart_id sent to the success page
	if cart_id == order_cart_id:
		#return the payment_status
		payment_status = order_extras.get_cart_id_payment_status(order_cart_id)

	return payment_status

def shop_success(request):

	#assume the worst, with these variables:
	success_header = global_extras.return_site_name
	success_message = "Oops! This is not the page you need."
	order_ref_message = ""
	order_ref = ""

	if request.method == 'GET':
		order_ref = request.GET.get('or')
		order_cart_id = request.GET.get('cid')
		#print(order_ref)
		#print(order_cart_id)

	#check if a checkout_started flag is set in the session
	is_on = cart_extras.get_checkout_started_session_variable(request)

	#note here that it's "TRUE" rather than True - this is because it's stored in the session as "TRUE" or "FALSE" (string)	
	if is_on == "TRUE":

		#to prevent any old address variables being entered, do a few checks before showing Thank You page
		if order_ref and order_cart_id:

			payment_status = payment_checks(request, order_ref,order_cart_id)
			payment_reference = order_extras.get_payment_method_ref(order_ref)

			#print("the payment_status on this success order is:")
			#print(payment_status)
			if payment_status == "PAID":
				#print("in here and I'm paid")
				success_header = "Thank you"
				success_message = "Your payment succeeded. Please check your email for confirmation."
				order_ref_message = "%s %sSDD%s" %("Your reference is: ", payment_reference, order_ref)
			elif payment_status == "PENDING":
				#print("in here and I'm pending")
				success_header = "Thank you for your order"
				success_message = "Your payment is being processed. <br>You will receive an email confirmation when your payment has succeeded and your order has been confirmed."
				order_ref_message = "%s %s" %("Please print this page to save your order reference: SSD", order_ref)
			elif payment_status == "FREE":
				#print("in here and I'm a free order")
				success_header = "Thank you for your order"
				success_message = "Your order is being processed."
				order_ref_message = "%s %s" %("Please print this page to save your order reference: SSD", order_ref)
			else:
				"in here and not pending or paid or free"
		else:
			print("in here and there was no order ref and cart_id")

	else:
		print("checkout started variable was not set to on")

	return render(request, 'shop/success.html',{"success_header": success_header,
		"success_message":success_message, "order_ref_message":order_ref_message})

def shop_cancelled(request):
	
	#assume the worst, with these variables:
	cancel_header = global_extras.return_site_name
	cancel_message = "Oops! This is not the page you need."
	order_ref_message = ""
	order_ref = ""

	if request.method == 'GET':
		order_ref = request.GET.get('or')
		order_cart_id = request.GET.get('cid')
		#print(order_ref)
		#print(order_cart_id)

		#check if a checkout_started flag is set in the session
		is_on = cart_extras.get_checkout_started_session_variable(request)

		#note here that it's "TRUE" rather than True - this is because it's stored in the session as "TRUE" or "FALSE" (string)	
		if is_on == "TRUE":
			print("it is on")
			#to prevent any old address variables being entered, do a few checks before showing the Cancelled Page
			if order_ref and order_cart_id:

				payment_status = payment_checks(request, order_ref,order_cart_id)
				#print("the payment_status on this cancelled order is:")
				#print(payment_status)
				if payment_status == "PENDING":
					#print("in here and I'm pending")
					#this page has correctly been raised from a cancelled payment
					#so, we want to keep the cart intact in case the user tries to pay again
					#so, turn off the flag that a checkout has been started
					cart_extras.turn_off_checkout_started_session_variable(request)
					#remove the 'PENDING' payment status in the order table, as it is no longer PENDING
					#this will prevent the site creating a new cart_id
					order_extras.update_order_after_payment_cancel(order_ref)
					#remove the order id from the discounts table IF it is there under a single_use discount code
					discount_extras.remove_single_use_order_id(order_extras.get_order(order_ref))
					cancel_message = "You have cancelled this order."
				else:
					print("in here and I'm not pending")

			else:
				print("in here and there was no order ref and cart_id")
		else:
			print("checkout started variable was not set to on")

	return render(request, 'shop/cancelled.html',{"cancel_header": cancel_header,"cancel_message":cancel_message})



