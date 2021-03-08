from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [

	path('add_to_cart/<int:product_id>/<int:quantity>/', views.add_to_cart, name="add_to_cart"), 
	path('view_cart/', views.view_cart, name="view_cart"), 
	path('checkout_cart/', views.checkout_cart, name="checkout_cart"), 
	path('update_cart/<int:product_id>/<int:quantity>/', views.update_cart, name="update_cart"),
	path('update_shipping_address/', views.update_shipping_address, name="update_shipping_address"),
	path('update_delivery_details/', views.update_delivery_details, name="update_delivery_details"),
	path('update_discount_code/', views.update_discount_code, name="update_discount_code"),
	path('update_postage_details/<str:postageType>/', views.update_postage_details, name="update_postage_details"),
	path('get_postage_options/', views.get_postage_options, name="get_postage_options"),
	path('delete_item/<int:product_id>/', views.delete_item, name="delete_item"), 
	path('get_country/<str:country_code>/', views.get_country, name="get_country"),
	path('order_summary/', views.order_summary, name="order_summary"),
	path('create_checkout_session/<str:paymentMethod>/<str:coupon>/', views.create_checkout_session, name="create_checkout_session"),
	path('create_checkout_session/<str:paymentMethod>/', views.create_checkout_session, name="create_checkout_session"),
	path('create_stripe_coupon/', views.create_stripe_coupon, name="create_stripe_coupon"),
	path('process_order/', views.process_order, name="process_order"),
	path('stripe_webhook/', views.stripe_webhook, name="stripe_webhook"),
	path('paypal_webhook/', views.paypal_webhook, name="paypal_webhook"),
		
]