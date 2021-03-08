from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

class CartDefault(models.Model):

	class Meta:
		app_label = "carts"

	max_per_cart = models.PositiveSmallIntegerField(verbose_name="Max Items Allowed per Cart",validators = [MinValueValidator(1)], default=5)
	date_created = models.DateTimeField(default=timezone.now)
	last_edited = models.DateTimeField(auto_now=True)

	def __str__(self):
		return "%s" % (self.id)







