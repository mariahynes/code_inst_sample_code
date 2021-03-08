from django.contrib import admin
from .models import Order, OrderItem
from shipping.models import Region, PostageRate, CountryRegion
from products.models import Product

class OrderItemInline(admin.TabularInline):
	model=OrderItem
	extra = 1
	max_num = 2
	can_delete = False
	show_change_link = False
	classes = ['collapse',]
	fields = (('order_ID'),
		('product_ID'),
		('current_product_price'),
		('product_price_for_order'),
		('product_quantity'),
		('product_discount_code'),
		('product_subtotal'),
		('product_discount_total'),
		('product_total'))
	readonly_fields = ('current_product_price','product_subtotal','product_total')
	

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	
	inlines=[
		OrderItemInline, 
	]

	readonly_fields = ('id',
					'cart_ID',
					'date_ordered',
					'last_edited',
					'order_subtotal_amount',
					'order_total_amount',
					'sub_total_from_cart',
					'shipping_type_from_cart',
					'shipping_total_from_cart',
					'final_total_from_cart',
					'order_and_merchant_totals_match',
					'payment_ref_from_method',
					'payment_status',
					'payment_succeeded_amount',
					'payment_succeeded_date',
					'payment_refunded_amount',
					'payment_refunded_date',
					'payment_ref_from_refund',
					'billing_name','billing_email','billing_paypal_payer_id',
					'billing_address_line1', 
					'billing_address_line2', 
					'billing_address_state',
					'billing_address_city',
					'billing_address_postal_code',
					'billing_address_country',

					'order_confirmation_sent_to_customer', 
					'date_order_confirmation_sent_to_customer',
					'order_confirmation_sent_to_shop',
					'date_order_confirmation_sent_to_shop',

					'payment_refund_sent_to_customer',
					'date_payment_refund_sent_to_customer',
					'payment_refund_sent_to_shop',
					'date_payment_refund_sent_to_shop',

					'payment_failed_sent_to_customer', 
					'date_payment_failed_sent_to_customer',
					'payment_failed_sent_to_shop',
					'date_payment_failed_sent_to_shop')

	list_display = ('id',
					'date_ordered',
					'order_subtotal_amount',
					'shipping_total',
					'discount_total',
					'order_total_amount',
					'order_complete',
					'order_refunded',
					'payment_method')
	ordering = ('-last_edited',
				'date_ordered',
				'payment_ref_from_method',)
	search_fields=('payment_ref_from_method',
				'billing_email',)
	list_filter=('order_complete', 
				'payment_method', 
				'order_posted')
	fieldsets=(
		('Order Status', {

			'description': "<br><b>NB: Only 'completed' orders will affect stock levels</b><br><br>", 
			'fields':(('id'),
					('order_complete','order_refunded'),
					('date_ordered','last_edited'))
			}),

		('Order Summary', {
			'classes': ('extrapretty','wide'),
			'description': "<br><b>Order Details</b><br><br><input type='submit' value='Refresh' name='_continue'>", 
			'fields':(('payment_method'),
					('order_subtotal_amount'),
					('shipping_total','shipping_type'), 
					('discount_total','order_discount_code'), 
					('order_total_amount'),
					('order_and_merchant_totals_match'),
					('order_posted'), 
					('order_posted_date'),
					('shipping_reference')),
			}),

		('Cart Summary', {
			'classes': ('collapse',),
			'description': "<br><b>Cart Details (if applicable)</b><br><br>", 
			'fields':(('cart_ID'),
					('sub_total_from_cart'),
					('shipping_type_from_cart'),
					('shipping_total_from_cart'),
					('final_total_from_cart'))
			}),

		('Shipping Information (if applicable)', {

			'classes': ('collapse',),
			'description': "<br><b>Delivery Information (incl. Customer/Order Notes):</b><br><br>", 
			'fields':(('shipping_name'),
					('shipping_address_line1'), 
					('shipping_address_line2'), 
					('shipping_address_state'),
					('shipping_address_city'),
					('shipping_address_postal_code'),
					('shipping_address_country'),
					('customer_notes'))
			}),
		('Payment Merchant Fields (if applicable)', {

			'classes': ('collapse',),
			'description': "<br><b>These fields are updated automatically if payment has been made via Stripe/Paypal:</b><br><br>", 
			'fields':(('payment_ref_from_method','payment_ref_from_refund'),
					('payment_status'),
					('payment_succeeded_amount'),
					('payment_succeeded_date'),
					('payment_refunded_amount'),
					('payment_refunded_date'),
					('billing_name','billing_email','billing_paypal_payer_id'),
					('billing_address_line1'), 
					('billing_address_line2'), 
					('billing_address_state'),
					('billing_address_city'),
					('billing_address_postal_code'),
					('billing_address_country'),
					('order_confirmation_sent_to_customer', 'date_order_confirmation_sent_to_customer'),
					('order_confirmation_sent_to_shop','date_order_confirmation_sent_to_shop'),
					('payment_refund_sent_to_customer', 'date_payment_refund_sent_to_customer'),
					('payment_refund_sent_to_shop','date_payment_refund_sent_to_shop'),
					('payment_failed_sent_to_customer','date_payment_failed_sent_to_customer'),
					('payment_failed_sent_to_shop','date_payment_failed_sent_to_shop'))
			}),


	)

#order_confirmation_sent_to_customer

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):


	fields = (('order_ID'),
		('product_ID'),
		('current_product_price'),
		('product_price_for_order'),
		('product_quantity'),
		('product_discount_code'),
		('product_subtotal'),
		('product_discount_total'),
		('product_total'),
		('date_ordered'),
		('last_edited'))
	readonly_fields = ('id','date_ordered','last_edited','current_product_price','product_subtotal','product_total')
	list_display = ('id','date_ordered', 'product_ID','current_product_price','product_price_for_order','product_quantity',
					'product_discount_code','product_subtotal','product_discount_total','product_total')
	ordering = ('-last_edited','date_ordered',)
	search_fields=('is_pending','date_ordered','product_ID')
	list_filter=('date_ordered', 'product_ID')



