from django.db import models
from django.utils import timezone


# Create your models here.

class Product(models.Model):

	class Meta:
		app_label = "products"

	product_display_name = models.CharField(verbose_name="Name of Product", max_length=255, blank=False)
	product_description = models.CharField(verbose_name="Short Description of Product", max_length=255, blank=False)
	product_long_description = models.TextField(verbose_name="Long Description of Product", blank=False, default="Enter the detailed description the customer will see on the Product page")
	product_price = models.DecimalField(verbose_name = "Price", blank=False, max_digits=6,decimal_places=2)
	product_price_currency = models.CharField(verbose_name="Price Currency", max_length=3, blank=False, default="EUR")
	stock_manufactured = models.PositiveSmallIntegerField(verbose_name="Manufactured", default=0)
	max_per_cart = models.PositiveSmallIntegerField(verbose_name="Max Allowed per Order (not used if zero)", default=0)
	product_image_1 = models.ImageField(upload_to='shady_dog_product_images', verbose_name="Product Image 1", blank=True, null=True)
	product_image_2 = models.ImageField(upload_to='shady_dog_product_images', verbose_name="Product Image 2", blank=True, null=True)
	product_image_3 = models.ImageField(upload_to='shady_dog_product_images', verbose_name="Product Image 3", blank=True, null=True)
	product_image_4 = models.ImageField(upload_to='shady_dog_product_images', verbose_name="Product Image 4", blank=True, null=True)
	product_image_1_desc = models.CharField(verbose_name="Product Image 1 Description", max_length=255, blank=True, null=True)
	product_image_2_desc = models.CharField(verbose_name="Product Image 2 Description", max_length=255, blank=True, null=True)
	product_image_3_desc = models.CharField(verbose_name="Product Image 3 Description", max_length=255, blank=True, null=True)
	product_image_4_desc = models.CharField(verbose_name="Product Image 4 Description", max_length=255, blank=True, null=True)
	product_image_sirv_1 = models.URLField(verbose_name="Product Image Sirv 1", blank=True, null=True, unique=True)
	product_image_sirv_1_desc = models.CharField(verbose_name="Product Image Sirv 1 Description", max_length=255, blank=True, null=True)
	product_image_sirv_2 = models.URLField(verbose_name="Product Image Sirv 2", blank=True, null=True, unique=True)
	product_image_sirv_2_desc = models.CharField(verbose_name="Product Image Sirv 2 Description", max_length=255, blank=True, null=True)
	product_image_sirv_3 = models.URLField(verbose_name="Product Image Sirv 3", blank=True, null=True, unique=True)
	product_image_sirv_3_desc = models.CharField(verbose_name="Product Image Sirv 3 Description", max_length=255, blank=True, null=True)
	product_image_sirv_4 = models.URLField(verbose_name="Product Image Sirv 4", blank=True, null=True, unique=True)
	product_image_sirv_4_desc = models.CharField(verbose_name="Product Image Sirv 4 Description", max_length=255, blank=True, null=True)
	product_image_sirv_5 = models.URLField(verbose_name="Product Image Sirv 5", blank=True, null=True, unique=True)
	product_image_sirv_5_desc = models.CharField(verbose_name="Product Image Sirv 5 Description", max_length=255, blank=True, null=True)
	date_created = models.DateTimeField(default=timezone.now)
	last_edited = models.DateTimeField(auto_now=True)
	is_activated = models.BooleanField(blank=True, verbose_name="is this product activated?", default=False)

	def __str__(self):
		return "%s" % (self.product_display_name)