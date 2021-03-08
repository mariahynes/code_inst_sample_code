from django.db import models
from products.models import Product
from orders.models import Order
from django.utils import timezone

class Discount(models.Model):

	DISCOUNT_TYPES = (
		('SHIPPING', 'SHIPPING'),
		('ORDER', 'ORDER'),
		('PRODUCT', 'PRODUCT'),
	)

	USAGE_FREQUENCY = (
		('SINGLE_USE', 'SINGLE USE'),
		('MULTI_USE', 'MULTI USE'),
	)

	def discount_desc(self):

		the_description = ""
		the_percent = self.discount_percentage
		the_type = self.discount_type

		if self.product_id:

			product_name = self.product_id.product_display_name

		else:

			product_name = ""

		the_product = self.product_id

		the_percent_formatted = "{:.0%}".format(the_percent)

		if the_type == "SHIPPING":

			the_type = "Shipping"

		if the_type == "ORDER":

			the_type = "your Order"

		if the_type == "PRODUCT":

			the_type = product_name

		the_description = "%s off %s" %(the_percent_formatted, the_type)

		return the_description

	def is_active(self):

		current_time = timezone.now()
		from_date = self.valid_from
		until_date = self.valid_until

		if (current_time >= from_date) and (current_time <= until_date):
			is_active = True
		else:
			is_active = False

		return is_active

	def is_expired(self):

		current_time = timezone.now()
		until_date = self.valid_until

		if (current_time > until_date):
			is_expired = True
		else:
			is_expired = False

		return is_expired

	def is_available(self):

		if self.is_active():

			if self.usage_frequency == "SINGLE_USE":

				if self.used_by_order_id:
					is_available = False
				else:
					is_available = True

			elif self.usage_frequency == "MULTI_USE":
				
				is_available = True
				
		else:

			is_available = False

		return is_available

	is_active.boolean = True
	is_expired.boolean = True
	is_available.boolean = True
	#discount_desc = models.CharField(verbose_name="Discount Display Text", max_length=100, blank=False)
	class Meta:
		app_label = "discounts"

	discount_code = models.CharField(primary_key=True, max_length=8,verbose_name="Discount Code")
	discount_type = models.CharField(verbose_name="Discount Type", max_length=8, choices=DISCOUNT_TYPES, default="ORDER")
	discount_percentage = models.DecimalField(verbose_name = "Discount % (NB: 1 == 100%)", blank=False, max_digits=6,decimal_places=2, default=0)
	product_id = models.ForeignKey(Product, verbose_name="Product (if applicable)", on_delete=models.CASCADE, blank=True, null=True)
	valid_from = models.DateTimeField(verbose_name="Valid From",default=timezone.now)
	valid_until = models.DateTimeField(verbose_name="Valid Until")
	usage_frequency = models.CharField(verbose_name="Usage Frequency", max_length=128,choices=USAGE_FREQUENCY, default="MULTI_USE")
	used_by_order_id = models.ForeignKey(Order, verbose_name="Order ID (applicable only for single use)", on_delete=models.CASCADE, blank=True, null=True)
	date_created = models.DateTimeField(default=timezone.now)
	last_edited = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.discount_code
