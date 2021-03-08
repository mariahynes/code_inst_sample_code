from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse
import products.templatetags.product_extras as product_extras
import orders.templatetags.order_extras as order_extras
import shop.templatetags.global_extras as global_extras
import carts.templatetags.cart_extras as cart_extras
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


def show_product(request, product_id, quantity=1):

	request.session.set_test_cookie()
	
	the_product = product_extras.get_product(product_id)
	num_images = 4	
	units_sold = order_extras.get_product_units_sold(product_id)
	
	return render(request, 'products/product_details.html', {"product": the_product, "quantity":quantity, "units_sold":units_sold, "num_images": range(num_images) })

def try_product(request, product_id, quantity=1):

	the_product = product_extras.get_product(product_id)
	num_images = 4	
	units_sold = order_extras.get_product_units_sold(product_id)
	
	return render(request, 'products/product_try.html', {"product": the_product, "quantity":quantity, "units_sold":units_sold, "num_images": range(num_images) })
