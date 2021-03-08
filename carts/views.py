from django.shortcuts import render,redirect
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.http.response import JsonResponse, HttpResponse,HttpResponseRedirect
from orders.forms import ShippingAddressForm, CustomerNotesForm, PostageTypeForm, DiscountCodeForm
import products.templatetags.product_extras as product_extras
import orders.templatetags.order_extras as order_extras
import shop.templatetags.global_extras as global_extras
import carts.templatetags.cart_extras as cart_extras
import shipping.templatetags.shipping_extras as shipping_extras
import discounts.templatetags.discount_extras as discount_extras
from django.views.decorators.http import require_POST
from datetime import datetime
import stripe
import json
from shop.PayPalCreateOrder import CreateOrder
from shop.PayPalCaptureOrder import CaptureOrder
import paypalrestsdk
import dateutil.parser
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

def view_cart(request):
	
	cart_id = cart_extras.get_cart_id(request)
	cart_items = []
	total_quantity = 0

	if cart_id:

		cart_items_object = cart_extras.get_cart_items_object(request)

		for item in cart_items_object:
			item_details = cart_extras.get_item_values_in_cart(request, item)
			#print(item_details)
			cart_items.append(item_details)

		total_quantity = cart_extras.get_total_quantity_in_cart(request)
			
	return render(request, 'carts/view_cart.html', {"cart_id": cart_id, "the_cart": cart_items, "count_cart_items": total_quantity})

def checkout_cart(request):
	
	page_pop_up_message = ""

	if 'validation_message' in request.session:
		page_pop_up_message = (request.session['validation_message'])
		request.session['validation_message'] = ""
	else:
		page_pop_up_message = ""

	cart_id = cart_extras.get_cart_id(request)
	shipping_address_obj = cart_extras.get_shipping_address_object(request)
	shipping_delivery_details_obj = cart_extras.get_shipping_delivery_details_object(request)
	shipping_postage_obj = cart_extras.get_shipping_postage_details_object(request)
	discount_details_obj = cart_extras.get_cart_discount_details_object(request)

	cart_items = []
	shipping_address = {}
	total_quantity = 0
	shipping_address_form = []
	delivery_details_form = []
	postage_type_form = []
	discount_form = []
	the_cookie_message = ""
	selected_postage_type = ""

	if cart_id:

		cart_items_object = cart_extras.get_cart_items_object(request)

		for item in cart_items_object:
			item_details = cart_extras.get_item_values_in_cart(request, item)
			cart_items.append(item_details)
			
		total_quantity = cart_extras.get_total_quantity_in_cart(request)

		#can't checkout without shipping address	
		#get it from session if already saved
				
		shipping_address = shipping_address_obj
		delivery_details = shipping_delivery_details_obj
		postage_details =  shipping_postage_obj
		discount_details = discount_details_obj

		shipping_address_form = ShippingAddressForm(shipping_address)
		delivery_details_form = CustomerNotesForm(delivery_details)
		discount_form = DiscountCodeForm(discount_details)
		
		#this form never gets 'submitted' - it's only used for displaying CHOICE field values on the checkout page
		postage_type_form = PostageTypeForm(postage_details)

		#calculate shipping and final total
		selected_postage_type = cart_extras.get_postage_type(request)
		cart_shipping_total = cart_extras.calculate_shipping_cost_of_cart(request, selected_postage_type)
		cart_extras.add_or_update_cart_shipping_postage_details(request, selected_postage_type, cart_shipping_total)

		#calculate discount if code exists
		discount_details = cart_extras.calc_cart_discount_amount(request)
		if discount_details:
			cart_extras.add_or_update_discount_details(request, discount_details[1], discount_details[0], discount_details[3])

		cart_subtotal = cart_extras.calculate_cart_subtotal_in_cart(request)
		cart_final_total = cart_extras.calculate_final_total_in_cart(request)
		cart_extras.add_or_update_cart_totals(request,cart_subtotal, cart_final_total)
		
	else:
		return HttpResponseRedirect("/")
		#the_cookie_message = global_extras.prepare_template_as_string({"site_name":settings.SITE_DISPLAY_NAME}, "cookie_check_message.html")

	return render(request, 'carts/checkout_cart.html', {"cart_id": cart_id, "the_cart": cart_items, 
		"count_cart_items": total_quantity,"shipping_address":shipping_address, 
		"shipping_address_form":shipping_address_form, "delivery_details_form":delivery_details_form, "discount_form":discount_form, "postage_type_form": postage_type_form,
		"selected_postage_type":selected_postage_type, "the_cookie_message":the_cookie_message, "page_pop_up_message":page_pop_up_message} )

def order_summary(request):
	
	page_pop_up_message = ""

	if 'validation_message' in request.session:
		page_pop_up_message = (request.session['validation_message'])
		request.session['validation_message'] = ""
	else:
		page_pop_up_message = ""

	missing_address_fields = ""
	field_noun = ""

	if request.method=="POST":
		
		if is_session_valid(request):
		
			missing_address_fields = check_missing_address_fields(request)

			if missing_address_fields:

				if "," in missing_address_fields:
					field_noun = "fields are"
				else:
					field_noun = "field is"

				message_to_user = "Please update your Shipping Address. The following " + field_noun + " missing: " + missing_address_fields
				
				request.session['validation_message'] = message_to_user				
				return HttpResponseRedirect('/checkout_cart/')

			else:

				cart_id = cart_extras.get_cart_id(request)
				cart_items = []
				shipping_address = []
				delivery_instructions = []
				postage_details = []
				final_to_pay = []

				if cart_id:
					
					cart_items_object = cart_extras.get_cart_items_object(request)

					for item in cart_items_object:
						item_details = cart_extras.get_item_values_in_cart(request, item)
						cart_items.append(item_details)

					shipping_address_obj = cart_extras.get_shipping_address_object(request)
					shipping_delivery_details_obj = cart_extras.get_shipping_delivery_details_object(request)
					shipping_postage_obj = cart_extras.get_shipping_postage_details_object(request)
					discount_details_obj = cart_extras.get_cart_discount_details_object(request)
					cart_final_cost = cart_extras.get_cart_final_total_object(request)

				else:

					return HttpResponseRedirect("/")
							
				return render(request, 'carts/order_summary.html', {"cart_id": cart_id, "the_cart": cart_items, "shipping_address": shipping_address_obj, 
					"discount_details":discount_details_obj,"delivery_instructions":shipping_delivery_details_obj, "postage_details":shipping_postage_obj, 
					"final_to_pay":cart_final_cost,"page_pop_up_message":page_pop_up_message})
		else:
			#session is corrupted
			message_to_user = "Somehow your cart has corrupted and we cannot proceed to payment. Please select your items again"
			request.session['validation_message'] = message_to_user
			return HttpResponseRedirect('/checkout_cart/')

	else:
		
		return HttpResponseRedirect("/")

def is_session_valid(request):

	validation_passed = False
	
	cart_ok = False
	shipping_ok = False
	final_total_ok = False
	
	cart_id = cart_extras.get_cart_id(request)
	
	cart_ok = cart_extras.validate_cart_items(request)
	shipping_ok = cart_extras.validate_shipping_postage_details_object(request)
	final_total_ok = cart_extras.validate_cart_final_total_object(request)

	#if all these are ok this means that the session fields all still exist and that there is non-zero final total
	#it also means that if the recorded shipping cost zero it is because the county has not yet been entered)

	if cart_ok and shipping_ok and final_total_ok:

		validation_passed = True

	return validation_passed

def check_missing_address_fields(request):

	missing_address_fields = ""
	
	shipping_address_obj = cart_extras.get_shipping_address_object(request)

	#check the address (user input)
	missing_address_details = cart_extras.validate_shipping_address_object(request)
	
	if missing_address_details:

		for x in missing_address_details:
			missing_address_fields += x + ", "

		#remove last comma
		missing_address_fields = missing_address_fields[0:-2]
		
	return missing_address_fields

def process_order(request):

	cart_id_for_ref = cart_extras.get_cart_id(request)

	if request.method == 'POST':

		data = json.loads(request.body.decode("utf-8"))
		order_total = data["order_total"]

		if order_total == "0.00":
			
			try:
				#this creates an 0.00 payment amount order without a payment merchant
				#create the order in Order Table (save cart/shipping details) and add related cart items to OrderItem table
				order_id = order_extras.create_order_from_cart(request,"FREE")
				
				if order_id:

					cart_extras.turn_on_checkout_started_session_variable(request)
					order_extras.update_order_to_complete(order_id)
					#send email to shop owner (customer doesn't get email because they haven't provided their email address)
					order_extras.prepare_order_email(order_id, "shop", "FREE")
					order_id_str = str(order_id)
					return_url_string = "?or=" + order_id_str + "&cid=" + cart_id_for_ref

				return JsonResponse({'return_url_string': return_url_string, 'order_created': True})

			except Exception as e:

				return JsonResponse({'error': str(e),'order_created': False})

		else:

			return JsonResponse({'error': str(e),'order_created': False})



@csrf_exempt
def create_stripe_coupon(request):

	#code to create a one-off Stripe coupon if a discount is being applied to an order
	disc_desc = cart_extras.get_cart_discount_desc(request)
	disc_amt = cart_extras.get_cart_discount_amount(request)	
	stripe.api_key = settings.STRIPE_SECRET_KEY

	couponCode = ""
	
	if not disc_amt == "0.00":
		
		disc_amt = float(disc_amt)
		#format the amt as an int for sending 
		disc_amt_int = int(disc_amt * 100)

		try:

			couponCode = stripe.Coupon.create(
				amount_off=disc_amt_int,
				duration = "once",
				currency = "EUR",
				name=disc_desc,
			)

			couponCode=couponCode['id']
			
			return JsonResponse({'couponCode': couponCode, 'success': True})

		except Exception as e:
			print("creating Stripe coupon didn't work: " + str(e))
			return JsonResponse({'error': str(e), 'success': False})
	else:

		return JsonResponse({'couponCode': couponCode, 'success': True})


@csrf_exempt
def create_checkout_session(request, paymentMethod, coupon=""):

	#create the order in Order Table (save cart/shipping details) and add related cart items to OrderItem table
	order_id = order_extras.create_order_from_cart(request, paymentMethod)

	if order_id:
		#prepare some variables for the API calls
		cart_id_for_ref = cart_extras.get_cart_id(request)	
		order_id_str = str(order_id)
		order_description = "(%s - %s)" %(settings.SITE_DISPLAY_NAME,order_id) 
		customer_notes = cart_extras.get_customer_notes(request)
		domain_url=settings.DOMAIN_URL

	if paymentMethod == "STRIPE":

		domain_url=settings.DOMAIN_URL
		stripe.api_key = settings.STRIPE_SECRET_KEY			

		if order_id>0:
			#quicker to create the line_items object from the session information 
			#rather than accessing the db
			formatted_line_items = cart_extras.format_cart_items_for_stripe(request)
			
			#NB: this session variable can only be 'updated' as the LAST THING before sending for checkout
			#(which is why it isn't done at the top of this function)
			#Once it is done, any call to the get_cart_id function will check this variable and will delete the cart if it's 'in use'
			#let the session know that the current cart is being sent for checkout
			cart_extras.turn_on_checkout_started_session_variable(request)	

			try:
				if coupon:

					checkout_session = stripe.checkout.Session.create(
						billing_address_collection='required',
						success_url=domain_url + 'success?or=' + order_id_str + '&cid=' + cart_id_for_ref + '&session_id={CHECKOUT_SESSION_ID}',
						cancel_url=domain_url + 'cancelled?or=' + order_id_str + '&cid=' + cart_id_for_ref + '&session_id={CHECKOUT_SESSION_ID}',
						payment_method_types=['card'],
						mode='payment',
						discounts=[{
						    'coupon': coupon,
						}],
						client_reference_id=order_id,
						line_items=formatted_line_items,
						payment_intent_data={
							"metadata": {
									'order_id': order_id,
									'order_description': order_description,
									'customer_notes': customer_notes
							}
						},
						
					)

				else:

					checkout_session = stripe.checkout.Session.create(
						billing_address_collection='required',
						success_url=domain_url + 'success?or=' + order_id_str + '&cid=' + cart_id_for_ref + '&session_id={CHECKOUT_SESSION_ID}',
						cancel_url=domain_url + 'cancelled?or=' + order_id_str + '&cid=' + cart_id_for_ref + '&session_id={CHECKOUT_SESSION_ID}',
						payment_method_types=['card'],
						mode='payment',
						client_reference_id=order_id,
						line_items=formatted_line_items,
						payment_intent_data={
							"metadata": {
									'order_id': order_id,
									'order_description': order_description,
									'customer_notes': customer_notes
							}
						},
						
					)

				return JsonResponse({'sessionId': checkout_session['id'], 'order_created': True, 'info':'Checkout successful'})

			except Exception as e:

				return JsonResponse({'error': str(e),'order_created': True, 'info':'Problem with Checkout'})

		else:
			#couldn't create the order so return without sending for payment
			return JsonResponse({'order_created': False, 'info':'Problem creating the Order'})

	else:
		#this is paypal now
		
		if order_id>0:	

			try:
				cancel_url = domain_url + 'cancelled?or=' + order_id_str + '&cid=' + cart_id_for_ref 
				return_url = domain_url + 'success?or=' + order_id_str + '&cid=' + cart_id_for_ref
				formatted_line_items = cart_extras.format_cart_items_for_paypal(request,order_id,cart_id_for_ref,order_description)
				
				#cancel_url is used here, but return_url is ignored because onApprove is being handled client-side for now
				#sending both urls anyway (even though return_url not being used by Paypal)
				response = CreateOrder().create_order(formatted_line_items, "Shady Dog", return_url, cancel_url,True)				
				paypal_id = ""
				paypal_id = response.result.id 
				cart_extras.turn_on_checkout_started_session_variable(request)

				#NB: return_url here is the one that javascript uses to redirect user when order is approved (client-side redirect)
				return JsonResponse({'id':paypal_id, 'return_url':return_url, 'order_id':order_id,'cart_id_for_ref':cart_id_for_ref,'order_created': True})
					
			except Exception as e:
				print("%s%s %s" %("paypal checkout error for order ", order_id, str(e)))
				return JsonResponse({'error': str(e),'order_created': True})

		else:
			#couldn't create the order so return without sending for payment
			return JsonResponse({'order_created': False})



def capture_paypal_transaction_NOT_USED(request):
	
	domain_url=settings.DOMAIN_URL

	if request.method == 'POST':

		data = json.loads(request.body.decode("utf-8"))
		paypal_id = data["orderID"]
		order_id = data["or"]
		cart_id = data["cid"]
		
		try:

			order_id_str = str(order_id)
			response = CaptureOrder().capture_order(paypal_id, True)
			print("the header")
			print(response.headers)
			print("the body")
			the_body = response.Result
			print(the_body)
			json_content = json.loads(the_body)
			print("the json body")
			print(json_content)
			
			print("the email address")
			print(response.result.payer.email_address)
			json_content = json.loads(the_body)
			#order_data_json = json.loads(response.body.decode("utf-8"))
			#print(order_data_json)
			#print("capture response is: " + order_data_json)
			success_url= domain_url + 'success?or=' + order_id_str + '&cid=' + cart_id 
			
			return JsonResponse({'order_data':json_content, 'success_url':success_url})
				
		except Exception as e:
			print(str(e))
			return JsonResponse({'error': str(e),'order_captured': False})


@require_POST
@csrf_exempt
def paypal_webhook(request):
	print("received paypal_webhook")

	body_unicode = request.body.decode('utf-8')

	try:
		#for logging purposes only
		event = json.loads(body_unicode)
		event_type = event['event_type']
		print("%s %s" %("event is:" , event_type))
	except:
		print("couldn't access event type")
		pass

	event_body=body_unicode
	headers = request.headers
	#reset event type for when webhook is verified
	event_type = None
	
	# Paypal-Transmission-Id in webhook payload header
	transmission_id = headers["Paypal-Transmission-Id"]
	# Paypal-Transmission-Time in webhook payload header
	timestamp = headers["Paypal-Transmission-Time"]
	# Webhook id created on Paypal
	webhook_id = settings.PAYPAL_WEBHOOK_ID
	# Paypal-Transmission-Sig in webhook payload header
	actual_signature = headers["Paypal-Transmission-Sig"]
	# Paypal-Cert-Url in webhook payload header
	cert_url = headers["Paypal-Cert-Url"]
	# PayPal-Auth-Algo in webhook payload header
	auth_algo = headers["PayPal-Auth-Algo"]
	

	paypalrestsdk.configure(dict(mode=settings.PAYPAL_MODE,client_id=settings.PAYPAL_CLIENT_ID,client_secret=settings.PAYPAL_CLIENT_SECRET))
	success = paypalrestsdk.WebhookEvent.verify(transmission_id, timestamp, webhook_id, event_body, cert_url, actual_signature, auth_algo)
	print("the verification is: ")
	print(success)

	if settings.PAYPAL_MODE == "sandbox":
		success = True #making it True for testing (as can't verify in test)

	if not success:

		return HttpResponse(status=400)

	else:

		event = json.loads(body_unicode)
		event_type = event['event_type']
		print("%s %s" %("I received: ", event_type))
		
		if event_type == "CHECKOUT.ORDER.APPROVED":
			print(event_type)
			#Paypal do not send billing address details in their api, 
			#update the Order table with the Customer Name and Email Address
			order_id = event['resource']['purchase_units'][0]['reference_id']
			first_name = event['resource']['payer']['name']['given_name']
			last_name = event['resource']['payer']['name']['surname']

			email_address = event['resource']['payer']['email_address']

			order_extras.update_order_billing_email(order_id, email_address)
			customer_name = "%s %s" %(first_name, last_name)
			order_extras.update_order_billing_name(order_id, customer_name)
			paypal_payer_id = event['resource']['payer']['payer_id']
			order_extras.update_order_billing_paypal_payer_id(order_id, paypal_payer_id)
			paypal_payer_country_code = event['resource']['payer']['address']['country_code']
			order_extras.update_order_billing_paypal_payer_country_code(order_id,paypal_payer_country_code)

		if event_type =='PAYMENT.CAPTURE.DENIED':

			#print(event_type)
						
			#order id is part of the custom_id field provided (format is: "order_id|cart_id")
			try:

				shop_id = event['resource']['custom_id']
				id_str = shop_id.split("|")
				order_id = id_str[0]
				#print("the order id is:")
				#print(order_id)

			except KeyError:
				print("custom_id is not a key")

			order_extras.update_order_after_payment_fail(order_id)
			order_extras.prepare_order_email(order_id, "shop", "FAILED")
			order_extras.prepare_order_email(order_id, "customer", "FAILED")
			#print("FAILED status updated on Order record")

		if event_type == "PAYMENT.CAPTURE.REFUNDED":

			#print(event_type)
			if event['resource']['status'] == "COMPLETED":

				refund_time_date = event['create_time']
				refund_time_date_object = dateutil.parser.isoparse(refund_time_date)
				refund_amount =  event['resource']['amount']['value']
				refund_id = event['resource']['id']

				#order id is part of the custom_id field provided (format is: "order_id|cart_id")
				try:

					shop_id = event['resource']['custom_id']
					id_str = shop_id.split("|")
					order_id = id_str[0]
					#print("the order id is:")
					#print(order_id)

				except KeyError:
					print("custom_id is not a key")

				order_extras.update_order_after_payment_refund(order_id, refund_amount,refund_id,refund_time_date_object)
				order_extras.prepare_order_email(order_id, "shop", "REFUNDED")
				order_extras.prepare_order_email(order_id, "customer", "REFUNDED")
				#print("REFUNDED status updated on Order record")

			else:
				
				print("event['resource']['status'] is not 'COMPLETED' on REFUND webhook")


		if event_type == "PAYMENT.CAPTURE.COMPLETED":

			#print(event_type)
			#print("Checkout Completed")

			#check if it's paid or not at this point (will be PAID unless site accepts async payment method)
			if event['resource']['status'] == "COMPLETED":

				payment_time_date = event['create_time']
				payment_time_date_object = dateutil.parser.isoparse(payment_time_date)
				payment_amount =  event['resource']['amount']['value']
				payment_id = event['resource']['id']

				#order id is part of the custom_id field provided (format is: "order_id|cart_id")
				try:

					shop_id = event['resource']['custom_id']
					id_str = shop_id.split("|")
					order_id = id_str[0]
					#print("the order id is:")
					#print(order_id)

				except KeyError:
					print("custom_id is not a key")

				order_extras.update_order_after_successful_payment(order_id,payment_amount,payment_id,payment_time_date_object)	
				order_extras.prepare_order_email(order_id, "shop")
				order_extras.prepare_order_email(order_id, "customer")		
			
			else:
				
				print("event['resource']['status'] is not 'COMPLETED' on Payment Complete Webhook")


		

	return HttpResponse(status=200)
	

@csrf_exempt
def stripe_webhook(request):
	print("received stripe_webhook")

	stripe.api_key = settings.STRIPE_SECRET_KEY
	endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
	payload = request.body
	sig_header = request.META['HTTP_STRIPE_SIGNATURE']
	event = None

	try:
		event = stripe.Webhook.construct_event(
			payload, sig_header, endpoint_secret
		)
	except ValueError as e:
		# Invalid payload
		print("%s %s" %("invalid stripe webhook payload:", str(e)))
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		# Invalid signature
		print("%s %s" %("invalid stripe webhook signature:", str(e)))
		return HttpResponse(status=400)

		
	if event['type']== 'payment_intent.succeeded':

		#print("Payment Intent Successful")
		#payment has gone through so can add the billing details to the order in the database
		#save the stripe object
		stripe_obj = event['data']['object']['charges']['data'][0]
		
		#pdate the Order table with the Billing Details
		order_extras.update_order_billing_details_STRIPE(stripe_obj)


	if event['type']=='payment_intent.payment_failed':

		#print("Payment Intent Failed")

		stripe_obj = event['data']['object']['charges']['data'][0]

		#order ID can be found in the metadata of the charges section of the Stripe Object
   		#this is primary key of the order in the database
		order_id = stripe_obj.metadata.order_id

		order_extras.update_order_after_payment_fail(order_id)
		order_extras.prepare_order_email(order_id, "shop", "FAILED")
		order_extras.prepare_order_email(order_id, "customer", "FAILED")
		print("FAILED status updated on Order record")


	if event['type']=='charge.refunded':

		stripe_obj = event['data']['object']
		order_id = stripe_obj.metadata.order_id

		refund_obj = event['data']['object']['refunds']['data'][0]
		
		if refund_obj.status == "succeeded":

			refund_amount =  refund_obj.amount
			refund_amount_formatted = refund_amount / 100
			refund_id = refund_obj.id
			refund_time_date = refund_obj.created
			refund_time_date_object = datetime.fromtimestamp(refund_time_date)

			order_extras.update_order_after_payment_refund(order_id,refund_amount_formatted,refund_id,refund_time_date_object)
			order_extras.prepare_order_email(order_id, "shop", "REFUNDED")
			order_extras.prepare_order_email(order_id, "customer", "REFUNDED")

		else:
			print("charge.refunded is not listed as 'succeeded'")


	# handle the checkout.session.completed event
	if event['type'] == 'checkout.session.completed':

		#print("Checkout Completed")
		stripe_obj = event['data']['object']

		#check if it's paid or not at this point (will be PAID unless site accepts async payment method)
		if stripe_obj.payment_status == "paid":

			payment_time_date = event['created']
			payment_time_date_object = datetime.fromtimestamp(payment_time_date)

			# unlike the payment_intent.succeeded event, 
			# here the order id can be taken from the object's client_reference_id 
			# (as provided by us in the checkout session)
			order_id = stripe_obj.client_reference_id	
			payment_amount =  stripe_obj.amount_total
			payment_amount_formatted = payment_amount / 100
			payment_intent_id = stripe_obj.payment_intent

			order_extras.update_order_after_successful_payment(order_id,payment_amount_formatted,payment_intent_id,payment_time_date_object)
			
			order_extras.prepare_order_email(order_id, "shop")
			order_extras.prepare_order_email(order_id, "customer")

		else:
			
			print("session.payment_status is not 'paid'")

	return HttpResponse(status=200)

def add_to_cart(request, product_id, quantity):

	if request.method == 'GET':
		
		if request.COOKIES:

			try:
				#if cart_id exists already, get it, if not create it
				cart_id = cart_extras.get_cart_id(request, True)
				
				#add to cart or update cart if product is already there
				quantity_added = cart_extras.add_cart_item(request, product_id, quantity)
				#print(quantity_added)
				items_count = cart_extras.get_total_quantity_in_cart(request)
				
				if quantity_added == 0:
					#no items added (cart max reached)
					return JsonResponse({'success': False, 'quantity_added':quantity_added,'new_items_count': items_count})
				else:
					#some (or all) items added as requested
					return JsonResponse({'success': True, 'quantity_added':quantity_added,'new_items_count': items_count})

			except Exception as e:
				print("Add to Cart Error is:" + str(e))
				return JsonResponse({'error': str(e)})

		else:

			#no cookies enabled so cannot add to cart
			try:
				the_cookie_message = global_extras.prepare_template_as_string({"site_name":settings.SITE_DISPLAY_NAME}, "cookie_check_message.html")
				return JsonResponse({'cookie_issue': True, 'cookie_message':the_cookie_message })

			except Exception as e:

				return JsonResponse({'error': str(e)})
	else:

		print("request is not GET")

def delete_item(request, product_id):

	if request.method == 'GET':

		if request.COOKIES:

			try:
				#get the cart_id (but unlike add_to_cart, don't create it if it's not there already - it should be there if it is being UPDATED)
				cart_id = cart_extras.get_cart_id(request)

				cart_extras.delete_cart_item(request, product_id)
				item_value = 0
				items_count = cart_extras.get_total_quantity_in_cart(request)
				cart_subtotal = cart_extras.calculate_cart_subtotal_in_cart(request)
				
				#a final check to see if the cart is empty
				#if it is, delete the cart entirely
				if items_count == 0:

					cart_extras.delete_cart(request)

				return JsonResponse({'success': True,'new_total': item_value, 'new_items_count': items_count, "cart_subtotal": cart_subtotal})

			except Exception as e:

				return JsonResponse({'error': str(e)})

		else:

			#no cookies enabled so cannot update cart
			try:
				the_cookie_message = global_extras.prepare_template_as_string({"site_name":settings.SITE_DISPLAY_NAME}, "cookie_check_message.html")
				return JsonResponse({'cookie_issue': True, 'cookie_message':the_cookie_message })

			except Exception as e:

				return JsonResponse({'error': str(e)})

def update_cart(request, product_id, quantity):
    
    #user NEEDS to have cookies enabled 
	if request.method == 'GET':

		if request.COOKIES:

			try:
				#get the cart_id (but unlike add_to_cart, don't create it if it's not there already - it should be there if it is being UPDATED)
				cart_id = cart_extras.get_cart_id(request)

				quantity_adjusted = cart_extras.update_cart_item(request, product_id, quantity)
				item_value = cart_extras.calculate_product_subtotal_in_cart(request, product_id)

				items_count = cart_extras.get_total_quantity_in_cart(request)
				cart_subtotal = cart_extras.calculate_cart_subtotal_in_cart(request)
				
				
				if (quantity_adjusted == 0):
					result = False
				else:

					result = True
					
				return JsonResponse({'success': result,'quantity_adjusted':quantity_adjusted,'new_total': item_value, 
					'new_items_count': items_count, "cart_subtotal": cart_subtotal})
				
			except Exception as e:

				return JsonResponse({'error': str(e)})

		else:

			#no cookies enabled so cannot update cart
			try:
				the_cookie_message = global_extras.prepare_template_as_string({"site_name":settings.SITE_DISPLAY_NAME}, "cookie_check_message.html")
				return JsonResponse({'cookie_issue': True, 'cookie_message':the_cookie_message })

			except Exception as e:

				return JsonResponse({'error': str(e)})

def update_shipping_address(request):

	if request.method == 'POST':
		form_data = json.loads(request.body.decode("utf-8"))

		sName = form_data.get('shipping_name',"")
		sLine1 = form_data.get('shipping_address_line1',"")
		sLine2 = form_data.get('shipping_address_line2',"")
		sCity = form_data.get('shipping_address_city',"")
		sState = form_data.get('shipping_address_state',"")
		sPostCode = form_data.get('shipping_address_postal_code',"")
		sCountry = form_data.get('shipping_address_country',"")
	
		if request.COOKIES:

			try:
				old_shipping_address = cart_extras.get_shipping_address_object(request)
				old_form_data = json.dumps(old_shipping_address)
				cart_extras.add_or_update_cart_shipping_address(request, sName, sLine1, sLine2, sCity, sState, sPostCode, sCountry)
				shipping_address = cart_extras.get_shipping_address_object(request)
				new_form_data = json.dumps(shipping_address)

				cart_id = cart_extras.get_cart_id(request)
				postage_type = cart_extras.get_postage_type(request)
				cart_shipping_total = cart_extras.calculate_shipping_cost_of_cart(request, postage_type)
				cart_extras.add_or_update_cart_shipping_postage_details(request, postage_type, cart_shipping_total)

				#calculate discount if code exists
				discount_amount = "0.00"
				discount_details = cart_extras.calc_cart_discount_amount(request)
				if discount_details:
					cart_extras.add_or_update_discount_details(request, discount_details[1], discount_details[0], discount_details[3])
					discount_amount =  discount_details[0]

				cart_subtotal = cart_extras.calculate_cart_subtotal_in_cart(request)
				cart_final_total = cart_extras.calculate_final_total_in_cart(request)
				cart_extras.add_or_update_cart_totals(request,cart_subtotal, cart_final_total)

				return JsonResponse({'success': True, 'new_form_data':new_form_data, 'old_form_data': old_form_data, 
					'cart_shipping_total':cart_shipping_total, "cart_final_total":cart_final_total, "discount_amount":discount_amount})

			except Exception as e:
				
				return JsonResponse({'error': str(e)})

		else:
			#no cookies enabled so cannot update shipping address
			try:
				the_cookie_message = global_extras.prepare_template_as_string({"site_name":settings.SITE_DISPLAY_NAME}, "cookie_check_message.html")
				return JsonResponse({'cookie_issue': True, 'cookie_message':the_cookie_message })

			except Exception as e:

				return JsonResponse({'error': str(e)})
	else:
		return HttpResponseRedirect("/")

def get_postage_options(request):

	if request.method == 'POST':
		
		postage_data = json.loads(request.body.decode("utf-8"))
		
		if request.COOKIES:

			try:
				postage_items = {}
				shipping_country = cart_extras.get_shipping_address_country(request)
				shipping_country_name = shipping_extras.get_country_name(shipping_country)
				cart_id = cart_extras.get_cart_id(request)
				items_count = cart_extras.get_total_quantity_in_cart(request)

				for item in postage_data:
					
					if shipping_country:
						
						postage_items[item] = shipping_extras.get_shipping_cost(shipping_country, items_count, item)
					else:
						
						postage_items[item] = "0.00"

				
				if shipping_country:
					result = True
				else:
					result = False

				return JsonResponse({'success': result, 'new_postage_data':postage_items, 'shipping_country':shipping_country, 'shipping_country_name':shipping_country_name})

			except Exception as e:
				
				return JsonResponse({'error': str(e)})

		else:
			#no cookies enabled so cannot update shipping address
			try:
				the_cookie_message = global_extras.prepare_template_as_string({"site_name":settings.SITE_DISPLAY_NAME}, "cookie_check_message.html")
				return JsonResponse({'cookie_issue': True, 'cookie_message':the_cookie_message })

			except Exception as e:

				return JsonResponse({'error': str(e)})
	else:
		return HttpResponseRedirect("/")

def update_delivery_details(request):

	if request.method == 'POST':

		form_data = json.loads(request.body.decode("utf-8"))

		sNotes = form_data.get('customer_notes',"")
	
		if request.COOKIES:

			try:
				
				old_delivery_details = cart_extras.get_shipping_delivery_details_object(request)
				old_form_data = json.dumps(old_delivery_details)

				cart_extras.add_or_update_cart_shipping_delivery_details(request, sNotes)
				delivery_details = cart_extras.get_shipping_delivery_details_object(request)
				new_form_data = json.dumps(delivery_details)
				
				return JsonResponse({'success': True, 'new_form_data':new_form_data, 'old_form_data': old_form_data})

			except Exception as e:
				
				return JsonResponse({'error': str(e)})

		else:

			#no cookies enabled so cannot update shipping address
			try:
				the_cookie_message = global_extras.prepare_template_as_string({"site_name":settings.SITE_DISPLAY_NAME}, "cookie_check_message.html")
				return JsonResponse({'cookie_issue': True, 'cookie_message':the_cookie_message })

			except Exception as e:

				return JsonResponse({'error': str(e)})
	else:
		return HttpResponseRedirect("/")

def update_discount_code(request):

	discount_percentage = 0
	discount_type = ""
	amount_before_discount = 0
	discount_amount = "0.00"
	discount_message = ""
	product_totals = []

	if request.method == 'POST':

		form_data = json.loads(request.body.decode("utf-8"))
		sCode = form_data.get('discount_code',"")
		
		if request.COOKIES:

			try:
				
				old_discount_details = cart_extras.get_cart_discount_details_object(request)
				old_form_data = json.dumps(old_discount_details)
										
				#check if code is blank (customer could be removing rather than updating)
				if sCode:

					#check if same code being added twice (should do nothing, but warn customer)
					if sCode != cart_extras.get_cart_discount_code(request):
						
						#remove the existing code first (if it exists) before adding new one so that 
						#final total calcs are at correct starting point for the new discount code
						cart_extras.reset_cart_discount_code(request)

						shipping_total = cart_extras.get_postage_cost(request)
						final_total = cart_extras.get_final_total(request)
						
						#prepare dict of product_id and totals currently in cart
						product_totals_obj = cart_extras.get_product_totals_obj(request)
						discount_details = discount_extras.get_discount_amount_and_message(sCode, discount_type, shipping_total, product_totals_obj, final_total)
						
						discount_amount = discount_details[0]
						discount_code = discount_details[1]
						discount_message = discount_details[2]
						discount_desc = discount_details[3]
						
						cart_extras.add_or_update_discount_details(request, discount_code, discount_amount, discount_desc)
						new_discount_details = cart_extras.get_cart_discount_details_object(request)
						
						new_form_data = json.dumps(new_discount_details)
						
					else:

						#code already provided to cart, no change but give warning
						discount_details = cart_extras.get_cart_discount_details_object(request)
						new_form_data = json.dumps(discount_details)
						discount_message = "This code is already applied"
						discount_amount = cart_extras.get_cart_discount_amount(request)

				else:
					#no code provided, so update to no code (i.e. the provided code of blank)
					discount_code = sCode
					cart_extras.add_or_update_discount_details(request, discount_code, "0.00", "No discount applied")
					discount_details = cart_extras.get_cart_discount_details_object(request)
					new_form_data = json.dumps(discount_details)
					discount_message = "Discount is 0.00"

				#final total is affected by discount so make sure to update
				cart_subtotal = cart_extras.calculate_cart_subtotal_in_cart(request)
				cart_final_total = cart_extras.calculate_final_total_in_cart(request)
				cart_extras.add_or_update_cart_totals(request,cart_subtotal, cart_final_total)

				return JsonResponse({'success': True, 'new_form_data':new_form_data, 'old_form_data': old_form_data, "discount_message":discount_message, "discount_amount": discount_amount,"cart_final_total":cart_final_total})

			except Exception as e:
				
				return JsonResponse({'error': str(e)})

		else:

			#no cookies enabled so cannot update
			try:
				the_cookie_message = global_extras.prepare_template_as_string({"site_name":settings.SITE_DISPLAY_NAME}, "cookie_check_message.html")
				return JsonResponse({'cookie_issue': True, 'cookie_message':the_cookie_message })

			except Exception as e:

				return JsonResponse({'error': str(e)})
	else:
		return HttpResponseRedirect("/")


def update_postage_details(request, postageType):

	#user NEEDS to have cookies enabled 
	if request.method == 'GET':

		if request.COOKIES:

			try:
				
				cart_id = cart_extras.get_cart_id(request)

				postage_fee = cart_extras.calculate_shipping_cost_of_cart(request, postageType)
				cart_extras.add_or_update_cart_shipping_postage_details(request,postageType,postage_fee)
				
				#calculate discount if code exists
				discount_amount = "0.00"
				discount_details = cart_extras.calc_cart_discount_amount(request)
				if discount_details:
					cart_extras.add_or_update_discount_details(request, discount_details[1], discount_details[0], discount_details[3])
					discount_amount =  discount_details[0]

				cart_subtotal = cart_extras.calculate_cart_subtotal_in_cart(request)
				cart_final_total = cart_extras.calculate_final_total_in_cart(request)
				cart_extras.add_or_update_cart_totals(request,cart_subtotal, cart_final_total)

				if (not postage_fee == "0.00"):
					
					result = True
				else:
					
					result = False
				
				return JsonResponse({'success': result,'postage_fee':postage_fee, "cart_final_total":cart_final_total, "discount_amount":discount_amount})
				
			except Exception as e:

				return JsonResponse({'error': str(e)})

		else:

			#no cookies enabled so cannot update cart
			try:
				the_cookie_message = global_extras.prepare_template_as_string({"site_name":settings.SITE_DISPLAY_NAME}, "cookie_check_message.html")
				return JsonResponse({'cookie_issue': True, 'cookie_message':the_cookie_message })

			except Exception as e:

				return JsonResponse({'error': str(e)})

def get_country(request,country_code):

	if request.method == 'GET':
		
		try:
			country_name = shipping_extras.get_country_name(country_code)
			
			return JsonResponse({'success': True,'country_name':country_name})

		except Exception as e:
			
			return JsonResponse({'error': str(e)})





