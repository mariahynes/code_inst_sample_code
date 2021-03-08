from django.db import models
from django.conf import settings
from products.models import Product
import products.templatetags.product_extras as product_extras
from django_countries.fields import CountryField
from django.utils import timezone
from django.db.models import Sum

# Create your models here.

class Order(models.Model):

	PAYMENT_METHODS = (
		('STRIPE', 'STRIPE'),
		('PAYPAL', 'PayPal'),
		('CASH', 'Cash'),
		('FREE', 'FREE'),
	)

	POSTAGE_TYPES = (
		('TK', 'Tracked'),
		('SD', 'Standard'),
		('XX', 'Free'),
	)

	PAYMENT_STATUS = (
		('PAID', 'PAID'),
		('FAILED', 'FAILED'),
		('PENDING', 'PENDING'),
		('CANCELLED', 'CANCELLED'),
		('FREE', 'FREE'),
		('REFUNDED', 'REFUNDED'),
	)

	def order_payment_method_link(self):

		#this is the link to the payment merchant (if applicable)
		payment_method_link = ""
		payment_ref = self.payment_ref_from_method

		if payment_ref:
			if self.payment_method == "STRIPE":
				if settings.STRIPE_MODE == "live":
					payment_method_link = settings.STRIPE_LIVE_PAYMENT_URL + payment_ref
				else:
					payment_method_link = settings.STRIPE_TEST_PAYMENT_URL + payment_ref

			elif self.payment_method == "PAYPAL":
				if settings.PAYPAL_MODE == "live":
					payment_method_link = settings.PAYPAL_LIVE_PAYMENT_URL + payment_ref
				else:
					payment_method_link = settings.PAYPAL_TEST_PAYMENT_URL + payment_ref
			else:
				payment_method_link = ""

		return payment_method_link

	def link_to_order(self):

		the_link = ""
		order_id = self.id
		order_id_str = str(order_id)
		the_link = settings.SITE_ORDER_URL + order_id_str

		return the_link

	def order_subtotal_amount(self):

		#this is the cost of the products only (after any product-level discounts applied)
		order_id = self.id
		the_subtotal = 0
		
		order_detail = OrderItem.objects.filter(order_ID=order_id)
		for order in order_detail:
			the_subtotal = the_subtotal + order.product_total()

		return the_subtotal

	def order_quantity(self):

		#this is the sum of the product_quantity field from OrderItem table
		order_id = self.id
		the_quantity = 0

		order_detail = OrderItem.objects.filter(order_ID=order_id)
		for order in order_detail:
			the_quantity = the_quantity + order.product_quantity

		return the_quantity
	
	def order_total_amount(self):

		order_id = self.id
		subtotal = self.order_subtotal_amount()
		shipping = self.shipping_total
		order_discount = self.discount_total

		full_total = (subtotal + shipping) - order_discount

		return full_total
		
	def order_and_merchant_totals_match(self):

		if (self.payment_ref_from_method):
			
			if ((self.order_total_amount()) == (self.payment_succeeded_amount)):

				return "YES"

			else:
				
				return "NO"
		else:

			return "Not applicable"


	class Meta:
		app_label = "orders"

	cart_ID = models.CharField(verbose_name="Cart ID", max_length=100,blank=True, null=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	last_edited = models.DateTimeField(auto_now=True)
	order_discount_code = models.CharField(verbose_name="Order Discount Code", max_length=10, blank=True, null=True)
	shipping_type = models.CharField(verbose_name="Shipping Type", max_length=2, choices=POSTAGE_TYPES)
	order_items = models.ManyToManyField(Product, through='OrderItem', through_fields=('order_ID','product_ID'))
	shipping_total = models.DecimalField(verbose_name = "Shipping Cost", max_digits=6,decimal_places=2, default=0)
	discount_total = models.DecimalField(verbose_name = "Discount Amount", max_digits=6,decimal_places=2, default=0)
	sub_total_from_cart = models.DecimalField(verbose_name = "Subtotal (from Cart)", max_digits=6,decimal_places=2, default=0)
	shipping_type_from_cart = models.CharField(verbose_name="Shipping Type (from Cart)", max_length=20, blank=True, null=True)
	shipping_total_from_cart = models.DecimalField(verbose_name = "Shipping Cost (from Cart)", max_digits=6,decimal_places=2, default=0)
	final_total_from_cart = models.DecimalField(verbose_name = "Total (from Cart)", max_digits=6,decimal_places=2, default=0)
	order_complete = models.BooleanField(verbose_name="Order Complete?", default=False)
	order_refunded = models.BooleanField(verbose_name="Order Refunded?", default=False)
	payment_method = models.CharField(verbose_name="Payment Method", max_length=6, choices=PAYMENT_METHODS)
	payment_status = models.CharField(verbose_name="Payment Status", max_length=12, choices=PAYMENT_STATUS)
	payment_succeeded_amount = models.DecimalField(verbose_name = "Payment Amount", max_digits=6,decimal_places=2,default=0)
	payment_succeeded_date = models.DateTimeField(blank=True, null=True)
	payment_ref_from_method = models.CharField(verbose_name="Payment Method Reference ID", max_length=255,blank=True, null=True)
	payment_refunded_amount = models.DecimalField(verbose_name = "Refund Amount", max_digits=6,decimal_places=2,default=0)
	payment_refunded_date = models.DateTimeField(blank=True, null=True)
	payment_ref_from_refund = models.CharField(verbose_name="Payment Refund Reference ID", max_length=255,blank=True, null=True)
	order_posted = models.BooleanField(verbose_name="Order has been posted/delivered?", default=False)
	order_posted_date = models.DateTimeField(verbose_name="Date Posted/Delivered", blank=True, null=True)
	shipping_reference = models.CharField(verbose_name="Shipping Reference Number", max_length=100,blank=True, null=True)
	billing_address_city = models.CharField(verbose_name="Billing Address City", max_length=255,blank=True, null=True)
	billing_address_country = CountryField(verbose_name="Billing Address Country", max_length=255,blank=True, null=True)
	billing_address_line1 = models.CharField(verbose_name="Billing Address Line1", max_length=255,blank=True, null=True)
	billing_address_line2 = models.CharField(verbose_name="Billing Address Line2", max_length=255,blank=True, null=True)
	billing_address_postal_code = models.CharField(verbose_name="Billing Address Postal Code", max_length=255,blank=True, null=True)
	billing_address_state = models.CharField(verbose_name="Billing Address State", max_length=255,blank=True, null=True)
	billing_email = models.CharField(verbose_name="Billing Email", max_length=255,blank=True, null=True)
	billing_name = models.CharField(verbose_name="Billing Name", max_length=255,blank=True, null=True)
	billing_phone = models.CharField(verbose_name="Billing Phone", max_length=255,blank=True, null=True)
	billing_paypal_payer_id = models.CharField(verbose_name="Payer ID (if PAYPAL)", max_length=255,blank=True, null=True, default="N/A")

	order_confirmation_sent_to_customer = models.BooleanField(verbose_name="Confirmation Email Sent to Customer?", default=False)
	date_order_confirmation_sent_to_customer = models.DateTimeField(verbose_name="Date Email Sent to Customer",blank=True, null=True)
	order_confirmation_sent_to_shop = models.BooleanField(verbose_name="Order Email Sent to Shop?", default=False)
	date_order_confirmation_sent_to_shop = models.DateTimeField(verbose_name="Date Email Sent to Shop",blank=True, null=True)

	payment_failed_sent_to_customer = models.BooleanField(verbose_name="Payment Failed Email Sent to Customer?", default=False)
	date_payment_failed_sent_to_customer = models.DateTimeField(verbose_name="Date Email Sent to Customer",blank=True, null=True)
	payment_failed_sent_to_shop = models.BooleanField(verbose_name="Payment Failed Email Sent to Shop?", default=False)
	date_payment_failed_sent_to_shop = models.DateTimeField(verbose_name="Date Email Sent to Shop",blank=True, null=True)

	payment_refund_sent_to_customer = models.BooleanField(verbose_name="Payment Refund Email Sent to Customer?", default=False)
	date_payment_refund_sent_to_customer = models.DateTimeField(verbose_name="Date Email Sent to Customer",blank=True, null=True)
	payment_refund_sent_to_shop = models.BooleanField(verbose_name="Payment Refund Email Sent to Shop?", default=False)
	date_payment_refund_sent_to_shop = models.DateTimeField(verbose_name="Date Email Sent to Shop",blank=True, null=True)

	shipping_address_city = models.CharField(verbose_name="Shipping Address City", max_length=255,blank=True, null=True)
	shipping_address_country = CountryField(verbose_name="Shipping Address Country",blank=True, null=True)
	shipping_address_line1 = models.CharField(verbose_name="Shipping Address Line1", max_length=255,blank=True, null=True)
	shipping_address_line2 = models.CharField(verbose_name="Shipping Address Line2", max_length=255,blank=True, null=True)
	shipping_address_postal_code = models.CharField(verbose_name="Shipping Address Postal Code", max_length=255,blank=True, null=True)
	shipping_address_state = models.CharField(verbose_name="Shipping Address State", max_length=255,blank=True, null=True)
	shipping_name = models.CharField(verbose_name="Shipping Name", max_length=255,blank=True, null=True)
	shipping_phone = models.CharField(verbose_name="Shipping Phone", max_length=255,blank=True, null=True)
	customer_notes = models.TextField(verbose_name="Notes from Customer/Order Notes",blank=True, null=True)

	def __str__(self):
		return "%s" % (self.id)


class OrderItem(models.Model):

	class Meta:
		app_label = "orders"

	def current_product_price(self):

		the_price = product_extras.get_product_price(self.product_ID_id)
		return the_price

	def product_subtotal(self):
		the_subtotal = self.product_quantity * self.product_price_for_order
		return the_subtotal

	def product_total(self):
		the_subtotal = self.product_subtotal()
		the_discount = self.product_discount_total
		the_total= the_subtotal - the_discount
		return the_total

	order_ID = models.ForeignKey(Order, on_delete=models.CASCADE)
	product_ID = models.ForeignKey(Product, on_delete=models.CASCADE)
	product_price_for_order = models.DecimalField(verbose_name = "Product Price Used", blank=False, max_digits=6,decimal_places=2, default=0)
	product_quantity = models.PositiveSmallIntegerField(verbose_name="Quantity", default=0)
	product_discount_code = models.CharField(verbose_name="Product Discount Code", max_length=10,blank=True, null=True)
	product_discount_total = models.DecimalField(verbose_name = "Discount Amount", blank=False, max_digits=6,decimal_places=2, default=0)
	date_ordered = models.DateTimeField(auto_now_add=True)
	last_edited = models.DateTimeField(auto_now=True)

	def __str__(self):
		return "%s %s | Quantity %s " % (self.order_ID, self.product_ID.product_display_name, self.product_quantity)



