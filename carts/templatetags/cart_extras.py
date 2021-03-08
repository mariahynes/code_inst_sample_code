from django import template
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from carts.models import CartDefault
import products.templatetags.product_extras as product_extras
import orders.templatetags.order_extras as order_extras
import shop.templatetags.global_extras as global_extras
import shipping.templatetags.shipping_extras as shipping_extras
import discounts.templatetags.discount_extras as discount_extras

register = template.Library()

def turn_on_checkout_started_session_variable(request):
	#flag to let session know that the cart has been sent to the checkout
	print("checkout started")
	request.session['checkout_started'] = "TRUE"

def turn_off_checkout_started_session_variable(request):
	if 'checkout_started' in request.session:
		print("checkout finished")
		del request.session['checkout_started']

def get_checkout_started_session_variable(request):

	the_answer = "False"
	if 'checkout_started' in request.session:
		the_answer = request.session['checkout_started']
	
	return the_answer

def get_existing_cart_id(request):
	#THIS IS USED ONLY BY LOGIN FUNCTION
	existing_cart_id = ""

	if 'existing_cart_id' in request.session:
		existing_cart_id = request.session['existing_cart_id']
	
	return existing_cart_id

def remove_existing_cart_id(request):
	if 'existing_cart_id' in request.session:
		del request.session['existing_cart_id']

def get_existing_cart_obj(request):
	#THIS IS USED ONLY BY LOGIN FUNCTION
	existing_cart_obj = []

	if 'existing_cart_obj' in request.session:
		existing_cart_obj = request.session['existing_cart_obj']
	
	return existing_cart_obj

def remove_existing_cart_obj(request):
	if 'existing_cart_obj' in request.session:
		del request.session['existing_cart_obj']

def get_cart_object(request, cart_id):
	cart_object = []

	#cart object is the session cookie id added as a session variable
	try:
		cart_object = request.session[cart_id]
	except:
		cart_object = []

	return cart_object

def print_cart_object(request):

	cart_id = get_cart_id(request)
	print(get_cart_object(request, cart_id))

def print_shipping_object(request):

	print(get_shipping_object(request))

def print_discount_object(request):
	
	print(get_cart_discount_details_object(request))

def get_cart_items_object(request):

	cart_items_object = []

	try:
		cart_id = get_cart_id(request)
		cart_items_object = request.session[cart_id]['cart_items']

	except KeyError:

		pass

	return cart_items_object

def get_cart_final_total_object(request):
	#was called get_shipping_final_total_object
	final_total_object = []
	#print_cart_object(request)
	try:
		cart_id = get_cart_id(request)
		final_total_object = request.session[cart_id]['cart_totals']

	except KeyError:

		pass

	return final_total_object

def get_cart_discount_details_object(request):

	discount_details_object = []
	try:
		cart_id = get_cart_id(request)
		discount_details_object = request.session[cart_id]['discount_details']
	except KeyError:
		pass

	return discount_details_object

def validate_cart_items(request):

	is_validated = True
	#there must be at least one item in the cart
	count_items = get_num_diff_products_in_cart(request)
	cart_items_object = get_cart_items_object(request)

	for item in cart_items_object:

		#check that all items have all their values
		product_id = get_product_id(request, item)
		product_name = get_product_name(request, item)
		product_quantity = get_product_quantity(request, item)

		if ((product_id == "" or product_id == 0) or (product_name == "") or (product_quantity == "" or product_quantity == 0)):
		
			is_validated = False
		

	if not is_validated:

		#delete the cart because the session has corrupted
		print("deleting the cart in cart_items")
		delete_cart(request)

	return is_validated

def get_shipping_object(request):

	shipping_object = []
	try:

		if 'shipping_details' in request.session:
			shipping_object = request.session['shipping_details']
	
	except KeyError:

		pass

	return shipping_object

def get_shipping_address_object(request):

	shipping_address_object = []

	try:
		shipping_address_object = request.session['shipping_details']['shipping_address']

	except KeyError:

		pass

	return shipping_address_object

def get_shipping_address_country(request):

	shipping_country_code = ""

	try:
		shipping_address_object = get_shipping_address_object(request)
		shipping_country_code = shipping_address_object['shipping_address_country']

	except KeyError:
		pass
	
	return shipping_country_code

def get_shipping_address_line1(request):

	shipping_address_line1 = ""

	try:
		shipping_address_object = get_shipping_address_object(request)
		shipping_address_line1 = shipping_address_object['shipping_address_line1']

	except KeyError:
		pass
	
	return shipping_address_line1

def get_shipping_address_line2(request):

	shipping_address_line2 = ""

	try:
		shipping_address_object = get_shipping_address_object(request)
		shipping_address_line2 = shipping_address_object['shipping_address_line2']

	except KeyError:
		pass
	
	return shipping_address_line2

def get_shipping_address_city(request):

	shipping_address_city = ""

	try:
		shipping_address_object = get_shipping_address_object(request)
		shipping_address_city = shipping_address_object['shipping_address_city']

	except KeyError:
		pass
	
	return shipping_address_city

def get_shipping_address_state(request):

	shipping_address_state = ""

	try:
		shipping_address_object = get_shipping_address_object(request)
		shipping_address_state = shipping_address_object['shipping_address_state']

	except KeyError:
		pass
	
	return shipping_address_state

def get_shipping_address_postal_code(request):

	shipping_address_postal_code = ""

	try:
		shipping_address_object = get_shipping_address_object(request)
		shipping_address_postal_code = shipping_address_object['shipping_address_postal_code']

	except KeyError:
		pass
	
	return shipping_address_postal_code

def get_shipping_address_name(request):

	shipping_address_name = ""

	try:
		shipping_address_object = get_shipping_address_object(request)
		shipping_address_name = shipping_address_object['shipping_name']

	except KeyError:
		pass
	
	return shipping_address_name

def validate_shipping_address_object(request):

	missing_data = []
	#mandatory fields are:
	# shipping_name
	# shipping_address_line1
	# shipping_address_city
	# shipping_address_postal_code
	# shipping_address_country

	if get_shipping_address_name(request) == "":
		missing_data.append("Name/Recipent")

	if get_shipping_address_line1(request) == "":
		missing_data.append("Address Line 1")

	if get_shipping_address_city(request) == "":
		missing_data.append("City")

	if get_shipping_address_postal_code(request) == "":
		missing_data.append("Postal Code")

	if get_shipping_address_country(request) == "":
		missing_data.append("Country")

	#print(missing_data)

	return missing_data

def get_shipping_delivery_details_object(request):

	delivery_details_object = []

	try:
		delivery_details_object = request.session['shipping_details']['delivery_details']

	except KeyError:

		pass

	return delivery_details_object

@register.simple_tag
def get_customer_notes(request):

	customer_notes = ""

	try:

		delivery_details_object = get_shipping_delivery_details_object(request)
		customer_notes = delivery_details_object['customer_notes']

	except KeyError:

		pass

	return customer_notes

def get_shipping_postage_details_object(request):

	postage_details_object = []

	try:
		postage_details_object = request.session['shipping_details']['postage_details']

	except KeyError:

		pass

	return postage_details_object

def get_postage_type(request):

	postage_type = ""

	try:

		delivery_details_object = get_shipping_postage_details_object(request)
		postage_type = delivery_details_object['postage_type']

	except KeyError:

		pass

	return postage_type

def get_postage_cost(request):
	# the SAVED shipping cost in cart
	# remember, do not use this for INITIALISING display value on checkout page 
	# (should always be recalculated when checkout page opens in case more items were to cart added since)

	postage_cost = ""

	try:

		delivery_details_object = get_shipping_postage_details_object(request)
		postage_cost = delivery_details_object['postage_cost']

	except KeyError:

		pass

	return postage_cost

def validate_shipping_postage_details_object(request):

	is_validated = True
	
	#these fields cannot have a blank value:
	#"postage_type"
	#"postage_cost"
	if get_postage_type(request) == "":
		is_validated = False

	if get_postage_cost(request) == "":
		is_validated = False

	#postage cost can only be "0.00" if the country field is blank (user hasn't entered it yet)
	if get_postage_cost(request) == "0.00":
		#check if there is a country field saved
		address_object = get_shipping_address_object(request)

		if not get_shipping_address_country(request) == "":
			#this means there IS a selected country so  the cart must be corrupted if there is no postage cost saved
			is_validated = False

	if not(is_validated):
		#print("deleting the cart in postage_cost")
		#delete the cart 
		cart_id = get_cart_id(request)
		delete_cart(request)

	return is_validated

@register.simple_tag
def get_cart_discount_code(request):

	discount_code = ""

	try:
		discount_details_object = get_cart_discount_details_object(request)
		discount_code = discount_details_object['discount_code']

	except KeyError:

		pass

	return discount_code

@register.simple_tag
def get_cart_discount_amount(request):

	discount_amount = "0.00"

	try:

		discount_details_object = get_cart_discount_details_object(request)
		discount_amount = discount_details_object['discount_amount']

	except KeyError:

		pass

	return discount_amount

@register.simple_tag
def get_cart_discount_desc(request):

	discount_desc = ""

	try:
		discount_details_object = get_cart_discount_details_object(request)
		discount_desc = discount_details_object['discount_desc']

	except KeyError:

		pass

	return discount_desc

def get_final_total(request):

	final_total = ""

	try:

		final_total_object = get_cart_final_total_object(request)
		final_total = final_total_object['final_total']

	except KeyError:

		pass

	return final_total

def get_sub_total(request):

	sub_total = ""

	try:

		final_total_object = get_cart_final_total_object(request)
		sub_total = final_total_object['sub_total']

	except KeyError:

		pass

	return sub_total

def validate_cart_final_total_object(request):

	is_validated = True
	
	#the sub_total cannot be a blank value (it's calculated)
	#the final_total cannot be a blank value (it's calculated)
	#they cannot have a "0.00" value either because this is the initialised value and 
	#they must have some value if there is something in the cart (both are calculated as soon as checkout page opens)
	
	if get_sub_total(request) == "" or get_sub_total(request) == "0.00":
		is_validated = False

	if get_final_total(request) == "" or get_final_total(request) == "0.00":
		#if final total is 0, this can only happen if there is a discount code and a discount amount
		if get_cart_discount_code(request) and get_cart_discount_amount(request):
			is_validated = True
		else:
			is_validated = False

	if is_validated == False:
		#delete the cart as it must be corrupted
		#print("deleting the cart in final_total")
		delete_cart(request)

	return is_validated

def get_latest_default_row_id():

	#the CartDefault table should only hold one row
	#but if in the event that it doesn't
	#return the id of the most recent row
	the_latest_row = CartDefault.objects.latest('last_edited')

	return the_latest_row.id

@register.simple_tag
def get_max_items_allowed_in_cart():

	latest_id = get_latest_default_row_id()
	
	max_allowed = 1

	the_default_row = CartDefault.objects.get(id=latest_id)

	max_allowed = the_default_row.max_per_cart

	return max_allowed

@register.simple_tag
def get_cart_id(request, create_cart=False):

	#returns the cart_id 
	#(option to use create_cart == True so that it will create a new cart if one doesn't exist)

	the_cart_id = ""

	try:
		#get the sessionid from the session (test cookie is set when someone views a product)
		the_session_id = request.COOKIES['sessionid']

		#check if this sessionid has been added to a session (this is a sign that a cart exists)
		if the_session_id in request.session:
			
			#cart exists
			#check if it is already associated with a successful order in the order table
			#if it is, generate new session id so that a new cart session can be started 
			#remove old cart data from the new session 
			#(because generating new sessionid with cycle_key will carry over previous session data)
			
			cart_session_used_in_checkout = get_checkout_started_session_variable(request)
			
			if cart_session_used_in_checkout == "TRUE":

				if(order_extras.get_cart_id_payment_status(the_session_id)):
					
					#new sessionID must be generated so that same cart ID is not used again
					turn_off_checkout_started_session_variable(request)
					request.session.cycle_key()
					#delete the cart in the session
					delete_cart(request)
					the_cart_id = ""

				else:
					#nothing was returned as payment_status from the order table 
					#so this sessionid/cart has not been in a checkout session before
					#can return the cart id
					the_cart_id = the_session_id

			else:
				
				the_cart_id = the_session_id

		else:
			#cart doesn't exist yet
			#print("the cart doesn't exist in this session")
			if create_cart:

				#create an empty cart with current sessionID as the key 
				# add empty cart_items 
				request.session[the_session_id] = {}
				request.session[the_session_id]['cart_items'] = {}
				request.session.modified = True

				#and add cart_totals object to it
				#MUST BE INITIALISED TO "0.00" so that it can never have blank value for final validation check
				cart_totals = {

						"sub_total": "0.00",
						"final_total": "0.00"

				}		
				request.session[the_session_id]['cart_totals'] = cart_totals
				request.session.modified = True

				#add discount object
				discount_details = {

					"discount_code": "",
					"discount_amount": "0.00",
					"discount_desc": ""
				}
				request.session[the_session_id]['discount_details'] = discount_details
				request.session.modified = True

				#initialise shipping details if they don't already exist
				#will keep them in the session so that they don't have to be entered again, only changed if needed
				if not 'shipping_details' in request.session:
					initialise_shipping_details(request)

				the_cart_id = the_session_id

			else:
				#could be that the cart IS in the session, but session has been reset due to a log in
				#a final check is to see if get_existing_cart_id and get_existing_cart_obj has values
				
				existing_cart_id = get_existing_cart_id(request)
				existing_cart_obj = get_existing_cart_obj(request)
				
				if existing_cart_id and existing_cart_obj:
					
					#there is a cart_id and object there
					#so add the cart_obj to the new session
					request.session[the_session_id] = existing_cart_obj
					the_cart_id = the_session_id
					
					#delete the existing
					remove_existing_cart_id(request)
					remove_existing_cart_obj(request)
				
	except KeyError:
		#test cookie did not get set (user has cookies disabled)
		#print("%s: %s" %("KEYERROR problem with this line: ", "the_session_id = request.COOKIES['sessionid']"))
		pass

	except:
		#print("%s: %s" %("There was an UNKNOWN problem with this line: ", "the_session_id = request.COOKIES['sessionid']"))
		pass

	return the_cart_id

def get_item_values_in_cart(request, item):
	
	item_values = {}
	#cast to string
	item = str(item)
	#this returns the VALUES of the dictionary where item is the KEY 
	#(if it exists)
	cart_items_object = get_cart_items_object(request)
	try:
		item_values = cart_items_object[item]
	except:

		item_values= {}
	
	return item_values

def get_product_id(request, item):
	
	#cast to string
	item = str(item)
	product_id = ""

	try:
		cart_item_values = get_item_values_in_cart(request, item)
		product_id = cart_item_values['product_id']

	except:

		product_id = ""	
	
	return product_id

def get_product_name(request, item):

	#cast to string
	item = str(item)
	product_name = ""

	try:
		cart_item_values = get_item_values_in_cart(request, item)
		product_name = cart_item_values['product_name']
	except:
		product_name = ""
	
	return product_name

def get_product_quantity(request, item):

	#cast to string
	item = str(item)
	product_quantity = 0
	
	try:
		cart_item_values = get_item_values_in_cart(request, item)
		product_quantity = cart_item_values['quantity']
	except:
		product_quantity = 0
	
	return product_quantity

def set_product_quantity(request, item, new_quantity):

	#cast to string
	item = str(item)
	product_quantity = 0

	try:
		product_details = get_item_values_in_cart(request, item)
		product_details['quantity'] = int(new_quantity)
		request.session.modified = True

	except:
		pass

	return product_quantity

def set_cart_item_object(request, product_id, product_name, product_quantity):

	product_details = {

		"product_id": product_id,
		"product_name": product_name,
		"quantity": product_quantity

	}

	cart_items_object = get_cart_items_object(request)
	cart_items_object[str(product_id)]=product_details
	request.session.modified = True

	return product_details

def initialise_shipping_details(request):

	request.session['shipping_details'] = {}

	shipping_address = {

			"shipping_name": "",
			"shipping_address_line1": "",
			"shipping_address_line2": "",
			"shipping_address_city": "",
			"shipping_address_state": "",
			"shipping_address_postal_code": "",
			"shipping_address_country": ""
	}

	delivery_details = {

			"customer_notes": ""
	}

	#postage_types as per saved in db - initialised here to 'TK' (Tracked)
	#postage_code MUST BE INITIALISED TO "0.00" so that it can never have blank value for final validation check
	postage_details = {

			"postage_type": "TK",
			"postage_cost": "0.00"
	}
						
	request.session['shipping_details']['shipping_address'] = shipping_address
	request.session.modified = True
	request.session['shipping_details']['delivery_details'] = delivery_details		
	request.session.modified = True
	request.session['shipping_details']['postage_details'] = postage_details		
	request.session.modified = True
	
def add_cart_item(request, product_id, quantity):
	
	cart_items_object = get_cart_items_object(request)
	current_quantity_in_cart = get_total_quantity_in_cart(request)
	max_allowed_in_cart_all_items = get_max_items_allowed_in_cart()
	
	#check if the product is in the cart already
	#assume it isn't
	product_exists = False
	the_item_object = {}

	item = str(product_id)
	the_item_values = get_item_values_in_cart(request,item)
	quantity_to_add = 0
	
	if the_item_values:		
		if the_item_values['product_id'] == product_id:
			product_exists = True

	if product_exists:
		
		item = str(product_id)
		product_quantity_already_ordered = get_product_quantity(request,item)
		
		#request is not from cart page, so the quantity provided is amount to be ADDED to the existing amount already in cart
		#check if it CAN be added to 

		quantity_to_add = return_validated_quantity(product_id, product_quantity_already_ordered, quantity, current_quantity_in_cart, max_allowed_in_cart_all_items)
		
		#it's not ok to just increase the quantity - check if limits will be affected
		if quantity_to_add > 0:

			new_quantity = product_quantity_already_ordered + quantity_to_add
			set_product_quantity(request, item, new_quantity)

	else:
		
		#product does not exist in the cart yet, so add it
		product_name = product_extras.get_product_name(product_id)
		product_quantity_already_ordered = 0

		# use the following function to check how much can be added (even though user has stated a quantity)
		quantity_to_add = return_validated_quantity(product_id, product_quantity_already_ordered, quantity, current_quantity_in_cart, max_allowed_in_cart_all_items)

		if quantity_to_add > 0:

			set_cart_item_object(request, product_id, product_name, quantity_to_add)
			
	new_sub_total = calculate_cart_subtotal_in_cart(request)
	new_final_total = calculate_final_total_in_cart(request)
	add_or_update_cart_totals(request, new_sub_total, new_final_total)

	return quantity_to_add

def validate_cart_totals(request):
	pass

def format_cart_items_for_paypal(request, order_id, cart_id, order_description):

	cart_items = get_cart_items_object(request)
	items=[]
	purchase_units=[]
	
	for item in cart_items:

		item_id_from_cart = get_product_id(request, item)
		item_name_from_cart = get_product_name(request, item)
		product_desc_from_shop = product_extras.get_product_description(item)
		product_sku = "SD_" + str(item_id_from_cart)
		item_quantity_from_cart = get_product_quantity(request, item)
		item_price_from_shop = product_extras.get_product_price(item_id_from_cart)
		item_price_currency_from_shop = product_extras.get_product_price_currency(item_id_from_cart)
		#format the price as an int for sending 
		item_price_from_shop = float(item_price_from_shop)
		item_price_from_shop = "{:.2f}".format(item_price_from_shop)
		line_item = {
			
			'name': item_name_from_cart,
			'description':product_desc_from_shop,
			'sku': product_sku,
			'unit_amount':{
				'currency_code': item_price_currency_from_shop,
				'value':item_price_from_shop
			},
			'tax': {
                  'currency_code': item_price_currency_from_shop,
                  'value': '0'
                },
			'quantity': item_quantity_from_cart
		}

		items.append(line_item)


	#totals info:

	sub_total = get_sub_total(request)
	final_total = get_final_total(request)

	#add shipping line item
	#shipping details for line item
	postage_type = get_postage_type(request)
	postage_type_display = shipping_extras.get_postage_type_display(postage_type)
	postage_cost = get_postage_cost(request)
	postage_cost = float(postage_cost)
	postage_cost = "{:.2f}".format(postage_cost)
	#postage_cost = float(postage_cost)
	#format the cost as an int for sending 
	#postage_cost_int = int(postage_cost)
	postage_currency = "EUR"
	shipping_logo = global_extras.get_logo_sirv_url()

	customer_name = get_shipping_address_name(request)
	address_line_1 = get_shipping_address_line1(request)
	address_line_2 = get_shipping_address_line2(request)
	city = get_shipping_address_city(request)
	state = get_shipping_address_state(request)
	postal_code = get_shipping_address_postal_code(request)
	country_code = get_shipping_address_country(request)
	custom_id = [str(order_id), str(cart_id)]
	custom_id = '|'.join(custom_id)
	delivery_instructions = get_customer_notes(request)
	
	#add discount line item (if it exists)
	discount_amount = '0'
	discount_code = get_cart_discount_code(request)
	if discount_code:
		discount_amount = get_cart_discount_amount(request)
		discount_amount = float(discount_amount)
		discount_amount = "{:.2f}".format(discount_amount)

	purchase_units=[{
		'reference_id': order_id,
        'description': order_description,
        'custom_id': custom_id,
        'amount':{
        	'currency_code': "EUR",
        	'value': final_total,
        	'breakdown': {
        		'item_total': {
        			'currency_code': 'EUR',
        			'value': sub_total
        		},
        		'shipping':{
        			'currency_code': 'EUR',
        			'value': postage_cost
        		},
        		'handling':{
                  'currency_code': 'EUR',
                  'value': '0'
                },
                'tax_total':{
                  'currency_code': 'EUR',
                  'value': '0'
                },
                'shipping_discount':{
                  'currency_code': 'EUR',
                  'value': '0'
                },
                'discount':{
                  'currency_code': 'EUR',
                  'value': discount_amount
                }
        	}
        },
        'items': items,				
		'shipping': {
			'method': postage_type_display,
			'name':{
				'full_name': customer_name
			},
			'address': {
				'address_line_1': address_line_1,
				'address_line_2': address_line_2,
				'admin_area_2': city,
				'admin_area_1': state,
				'postal_code': postal_code,
				'country_code': country_code
			}
		}
		
	}]

	return purchase_units

def format_cart_items_for_stripe(request):

	cart_items = get_cart_items_object(request)
	line_items = []

	for item in cart_items:

		item_id_from_cart = get_product_id(request, item)
		item_name_from_cart = get_product_name(request, item)
		item_quantity_from_cart = get_product_quantity(request, item)
		item_price_from_shop = product_extras.get_product_price(item_id_from_cart)
		item_price_currency_from_shop = product_extras.get_product_price_currency(item_id_from_cart)

		#format the price as an int for sending 
		item_price_from_shop = int(item_price_from_shop * 100)

		if product_extras.has_sirv_image(item_id_from_cart):
			item_image = product_extras.get_product_sirv_url(item_id_from_cart)
		else:
			item_image = product_extras.get_product_image_1(item_id_from_cart)
	
		line_item = {
			
			'price_data': {

				'unit_amount': item_price_from_shop,
				'currency': item_price_currency_from_shop,

				'product_data': {
					'name': item_name_from_cart,
					'images': [item_image],
					"metadata": {
						'product_id': item_id_from_cart,
					}
				},			

			},

			'quantity': item_quantity_from_cart,

		}

		line_items.append(line_item)

	#add shipping line item
	#shipping details for line item
	postage_type = get_postage_type(request)
	postage_type_display = shipping_extras.get_postage_type_display(postage_type)
	postage_cost = get_postage_cost(request)
	postage_cost = float(postage_cost)
	#format the cost as an int for sending 
	postage_cost_int = int(postage_cost * 100)
	postage_currency = "EUR"

	shipping_logo = global_extras.get_logo_sirv_url()

	#'name': "Shipping Cost (" + postage_type_display + ")",
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

	#print(line_items)
	return line_items						
		
def format_shipping_address_for_stripe(request):

	shipping_address = get_shipping_address_object(request)

	shipping = []

	shipping_details = {

		"address": {

			"name": shipping_address['shipping_name'],
			"line1": shipping_address['shipping_address_line1'],
			"line2": shipping_address['shipping_address_line2'],
			"city": shipping_address['shipping_address_city'],
			"state": shipping_address['shipping_address_state'],
			"postal_code": shipping_address['shipping_address_postal_code'],
			"country": shipping_address['shipping_address_country'],

		}

	}

	shipping.append(shipping_details)

	return shipping

def update_cart_item(request, product_id, quantity):

	product_details = {}
	cart_id = get_cart_id(request)
	cart_object = get_cart_object(request, cart_id)
	current_quantity_in_cart = get_total_quantity_in_cart(request)
	max_allowed_in_cart_all_items = get_max_items_allowed_in_cart()
	return_figure = 0

	#product_object = cart_object[str(product_id)]
	#product_quantity_already_ordered = product_object['quantity']
	item = str(product_id)
	product_quantity_already_ordered = get_product_quantity(request, item)

	#if from the cart page, then the quantity provided is not a 'NEW ADD'. It's the new amount in total. An increase/decrease of existing quantity.
	if (quantity < product_quantity_already_ordered):
		#if quantity is less than the existing amount, then it's to decrease existing quantity
		#it will be to reduce by 1 but still check the difference
		reduce_by = product_quantity_already_ordered - quantity	

		#it's ok to reduce the quantity - no limits will be affected
		new_quantity = product_quantity_already_ordered - reduce_by
		set_product_quantity(request, item, new_quantity)
		
		return_figure = -abs(reduce_by)

	else:
		#request is to increase quantity to the quantity provided
		increase_by = quantity - product_quantity_already_ordered
		#it's not ok to just increase the quantity - need to check if limits will be affected
		quantity_to_add = return_validated_quantity(product_id, product_quantity_already_ordered, increase_by, current_quantity_in_cart, max_allowed_in_cart_all_items)
		
		if quantity_to_add > 0:
			new_quantity = product_quantity_already_ordered + quantity_to_add
			set_product_quantity(request, item, new_quantity)

		return_figure =  quantity_to_add

	new_sub_total = calculate_cart_subtotal_in_cart(request)
	new_final_total = calculate_final_total_in_cart(request)
	add_or_update_cart_totals(request, new_sub_total, new_final_total)
	return return_figure

def return_validated_quantity(product_id, product_quantity_already_ordered, product_quantity_to_add, current_quantity_in_cart, max_allowed_in_cart_all_items):

	validated_quantity = 0
	
	# check the following:
	#1) whether the new total PRODUCT quantity in cart will exceed max allowed of the product in the cart
	#2) whether the new total quantity in cart will exceed max allowed in cart

	#check 1) 
	potential_quantity_of_product = product_quantity_already_ordered + product_quantity_to_add
	max_allowed_in_cart_this_item = product_extras.get_max_per_purchase(product_id)

	#max allowed of product could return 0 (which means ignore because no max is set)
	if max_allowed_in_cart_this_item > 0:

		#there IS a product limit set, so check it
		if potential_quantity_of_product <= max_allowed_in_cart_this_item:
			#ok so here, 1) has passed,
			#update product quantity as person wishes (subject to cart limits)
			validated_quantity = product_quantity_to_add
		else:
			#ok so here, 1) has failed,
			#only update product to what is left before reaching max allowed (subject to cart limits)
			validated_quantity = max_allowed_in_cart_this_item - product_quantity_already_ordered

	else:
		#ok so here, we see there is no limit set on a product level, 
		#so allowed to add requested quantity to the cart (subject to cart limits)
			
		validated_quantity = product_quantity_to_add

	
	#before sending back the validated_quantity (which will be added to existing quantity),
	#check 2) to see if the overall cart totals are still below limits should this update be made

	potential_quantity_in_cart = current_quantity_in_cart + validated_quantity
	
	if (potential_quantity_in_cart > max_allowed_in_cart_all_items):
	
		#then reduce to an amount that doesn't max out the cart
		cart_space_left = max_allowed_in_cart_all_items - current_quantity_in_cart

		validated_quantity = cart_space_left
		
	else:
		#no need to reduce, the amount as requested is fine
		validated_quantity = validated_quantity


	return validated_quantity


def add_or_update_cart_shipping_address(request, sName,sLine1,sLine2,sCity,sState,sPostCode,sCounty):
	
	shipping_details = {}
	shipping_object = get_shipping_address_object(request)
	
	#check if the shipping details are in the cart already
	if shipping_object:

		#print("shipping details already entered")
		shipping_object['shipping_name'] = sName
		shipping_object['shipping_address_line1'] = sLine1
		shipping_object['shipping_address_line2'] = sLine2
		shipping_object['shipping_address_city'] = sCity
		shipping_object['shipping_address_state'] = sState
		shipping_object['shipping_address_postal_code'] = sPostCode
		shipping_object['shipping_address_country'] = sCounty
		request.session.modified = True
		#print("shipping address details updated")

	else:
		#print("shipping details not already entered")
		#shipping details not already in the cart, so add them
		shipping_details = {

			"shipping_name": sName,
			"shipping_address_line1": sLine1,
			"shipping_address_line2": sLine2,
			"shipping_address_city": sCity,
			"shipping_address_state": sState,
			"shipping_address_postal_code": sPostCode,
			"shipping_address_country": sCounty
		}

		shipping_object = shipping_details
		request.session.modified = True
		#print("shipping address details added")

def add_or_update_cart_shipping_delivery_details(request, sNotes):
	
	delivery_details = {}
	delivery_details_object = get_shipping_delivery_details_object(request)
	
	#check if the shipping details are in the cart already
	if delivery_details_object:

		#print("delivery details already entered")
		delivery_details_object['customer_notes'] = sNotes
		request.session.modified = True
		#print("delivery details updated")

	else:
		#print("delivery details not already entered")
		#shipping details not already in the cart, so add them
		delivery_details = {

			"customer_notes": sNotes
		}

		delivery_details_object = delivery_details
		request.session.modified = True

		#print("delivery details added")

def add_or_update_cart_shipping_postage_details(request, sType, cost):

	postage_details = {}
	postage_details_object = get_shipping_postage_details_object(request)
	#print("the cost is: ")
	#print(cost)
	#check that cost, if 0 is stored as "0.00"
	if cost == 0:
		cost = "0.00"

	#print(cost)
	#check if the shipping details are in the cart already
	if postage_details_object:

		#print("postage details already entered")
		postage_details_object['postage_type'] = sType
		postage_details_object['postage_cost'] = str(cost)
		request.session.modified = True
		#print("postage details updated")

	else:
		#print("postage details not already entered")
		#postage details not already in the cart, so add them
		postage_details = {

			"postage_type": sType,
			"postage_cost": str(cost)
		}

		postage_details_object = postage_details
		request.session.modified = True

def add_or_update_discount_details(request, discount_code, discount_amount, discount_desc):

	discount_amount_str = str(discount_amount)
	
	discount_details_object = get_cart_discount_details_object(request)

	if discount_details_object:

		discount_details_object['discount_code'] = discount_code
		request.session.modified = True
		discount_details_object['discount_amount'] = discount_amount
		request.session.modified = True
		discount_details_object['discount_desc'] = discount_desc

	else:

		discount_details = {

			"discount_code": discount_code,
			"discount_amount": discount_amount_str,
			"discount_desc": discount_desc
		}

		discount_details_object = discount_details
		request.session.modified = True


def reset_cart_discount_code(request):

	add_or_update_discount_details(request, "", "0.00", "No discount applied")
	sub_total = calculate_cart_subtotal_in_cart(request)
	final_total = calculate_final_total_in_cart(request)
	add_or_update_cart_totals(request,sub_total,final_total)

def calc_cart_discount_amount(request):

	#remember what the code was
	discount_code = get_cart_discount_code(request)
	discount_details = {}

	if discount_code:

		#reset to update final total
		reset_cart_discount_code(request)
		
		shipping_total = get_postage_cost(request)
		final_total = get_final_total(request)
		product_totals_obj = get_product_totals_obj(request)
		discount_type = discount_extras.get_discount_type(discount_code)

		#use the original code and update the calcs
		discount_details = discount_extras.get_discount_amount_and_message(discount_code, discount_type, shipping_total, product_totals_obj, final_total)
		# FYI discount_details is made up of: 
		# discount_amount
		# discount_code
		# discount_message
		# discount_desc
		
	return discount_details


def add_or_update_cart_totals(request, sub_total, final_total):
	
	#save as strings
	subtotal_str = str(sub_total)
	final_total_str = str(final_total)

	cart_totals_object = get_cart_final_total_object(request)

	if cart_totals_object:
	
		cart_totals_object['sub_total'] = subtotal_str
		request.session.modified = True
		cart_totals_object['final_total'] = final_total
		request.session.modified = True

	else:
		
		cart_total_details = {
			"sub_total": subtotal_str,
			"final_total": final_total_str
		}

		cart_totals_object = cart_total_details
		request.session.modified = True

@register.simple_tag
def get_total_quantity_in_cart(request):

	# the sum of quantities of items in the entire cart
	quantity = 0
	cart_items_object = get_cart_items_object(request)

	for item in cart_items_object:
		#quantity = quantity + cart_object[item]['quantity']
		product_quantity = get_product_quantity(request, item)
		quantity = (quantity + product_quantity)
			
	return quantity

@register.simple_tag
def get_num_diff_products_in_cart(request):

	# the number of distinct items in the cart (not quantity of each)

	distinct_items = 0
	cart_items_object = get_cart_items_object(request)
	
	distinct_items = len(cart_items_object)
	#print("this is the number of items in the cart:")	
	#print(distinct_items)	

	return distinct_items

@register.simple_tag
def calculate_cart_subtotal_in_cart(request):

	# the cost of all items in the cart (just cost of products, not including shipping)

	total_price = 0
	cart_item_objects = get_cart_items_object(request)

	for item in cart_item_objects:
		product_id = get_product_id(request, item)
		item_price = product_extras.get_product_price(product_id)
		total_price = total_price + (get_product_quantity(request, item) * item_price)

	return total_price


@register.simple_tag
def calculate_product_subtotal_in_cart(request, item):

	# the cost of one product in the cart (not including shipping)
	#cast to string in order to look it up
	item = str(item)
	product_id = get_product_id(request,item)
	item_price = product_extras.get_product_price(product_id)

	subtotal = get_product_quantity(request, item) * item_price
	
	return subtotal

@register.simple_tag
def calculate_discount_in_cart(request):
	pass


def get_product_totals_obj(request):
	
	cart_item_objects = get_cart_items_object(request)
	product_totals = {}
	
	for item in cart_item_objects:
		
		product_id = get_product_id(request, item)		
		sub_total = calculate_product_subtotal_in_cart(request, item)

		product_totals[product_id] = sub_total

	return product_totals



@register.simple_tag
def calculate_shipping_cost_of_cart(request, postageType):
	
	# run this when checkout page opens - calculates based on number of items in the cart (IF a country is selected)

	shipping_cost = "0.00"
	country_code = get_shipping_address_country(request)
	
	if country_code:

		number_of_items = get_total_quantity_in_cart(request)

		if number_of_items >0:

			shipping_cost = shipping_extras.get_shipping_cost(country_code, number_of_items, postageType)

	return shipping_cost


@register.simple_tag
def calculate_final_total_in_cart(request):

	# sum of subtotal and shipping
	# less discount amount

	total = 0
	selected_postage_type = get_postage_type(request)
	
	if selected_postage_type:

		shipping = calculate_shipping_cost_of_cart(request,selected_postage_type)
		
	else:
		shipping = 0

	subtotal = calculate_cart_subtotal_in_cart(request)
	discount = get_cart_discount_amount(request)

	#shipping cost is stored as a string
	#sub_total is stored as a string
	#discount is stored as a string
	#convert before adding
	
	shipping_float = float(shipping)
	subtotal_float = float(subtotal)
	discount_float = float(discount)

	total = (shipping_float + subtotal_float) - discount_float
	total_formatted = "{:.2f}".format(total)

	return total_formatted




def delete_cart_item(request, item):

	item = str(item)
	cart_items_object = get_cart_items_object(request)
	
	try:

		del cart_items_object[item]
		request.session.modified = True
	
	except KeyError:

		print("this Cart item did not exist")


def delete_cart(request):
	
	cart_id = get_cart_id(request)
	
	try:

		del request.session[cart_id]
		
	except KeyError:

		print("this cart did not exist")
		
def delete_shipping(request):
	
	cart_id = get_cart_id(request)
	try:

		del request.session['shipping_details']

	except KeyError:

		print("shipping did not exist")

'''
	[{
                reference_id: "PUHF",
                description: "Sporting Goods",

                custom_id: "CUST-HighFashions",
                soft_descriptor: "HighFashions",
                amount: {
                    currency_code: "USD",
                    value: "230.00",
                    breakdown: {
                        item_total: {
                            currency_code: "USD",
                            value: "180.00"
                        },
                        shipping: {
                            currency_code: "USD",
                            value: "30.00"
                        },
                        handling: {
                            currency_code: "USD",
                            value: "10.00"
                        },
                        tax_total: {
                            currency_code: "USD",
                            value: "20.00"
                        },
                        shipping_discount: {
                            currency_code: "USD",
                            value: "10"
                        }
                    }
                },
                items: [{
                    name: "T-Shirt",
                    description: "Green XL",
                    sku: "sku01",
                    unit_amount: {
                         currency_code: "USD",
                         value: "90.00"
                    },
                    tax: {
                        currency_code: "USD",
                        value: "10.00"
                    },
                    quantity: "1",
                    category: "PHYSICAL_GOODS"
                },
                    {
                    name: "Shoes",
                    description: "Running, Size 10.5",
                    sku: "sku02",
                    unit_amount: {
                         currency_code: "USD",
                         value: "45.00"
                    },
                    tax: {
                        currency_code: "USD",
                        value: "5.00"
                    },
                    quantity: "2",
                    category: "PHYSICAL_GOODS"
                }
                ],
                shipping: {
                    method: "United States Postal Service",
                    address: {
                        name: {
                            full_name: "John",
                            surname: "Doe"
                        },
                        address_line_1: "123 Townsend St",
                        address_line_2: "Floor 6",
                        admin_area_2: "San Francisco",
                        admin_area_1: "CA",
                        postal_code: "94107",
                        country_code: "US"
                    }
                }
            }]
	'''