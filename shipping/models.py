from django.db import models
from django_countries.fields import CountryField
from django.utils import timezone

class Region(models.Model):

	REGIONS = (
		('IE', 'Ireland & Northern Ireland'),
		('GB', 'Great Britain'),
		('EUR', 'Europe'),
		('Z', 'Rest of the World'),
	)

	class Meta:
		app_label="shipping"

	region = models.CharField(primary_key=True,verbose_name="Region", max_length=3, choices=REGIONS, default="Z")

	def __str__(self):
		return self.get_region_display()

class CountryRegion(models.Model):

	REGIONS = (
		('IE', 'Ireland & Northern Ireland'),
		('GB', 'Great Britain'),
		('EUR', 'Europe'),
		('Z', 'Rest of the World'),
	)

	class Meta:
		app_label="shipping"

	country_code = CountryField(primary_key=True, verbose_name="Country")
	region = models.ForeignKey(Region,verbose_name="Region",on_delete=models.CASCADE)
	

class PostageRate(models.Model):

	POSTAGE_TYPES = (
		('TK', 'Tracked'),
		('SD', 'Standard'),
	)

	class Meta:
		app_label = "shipping"

	region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Postage Region")
	postage_type = models.CharField(verbose_name="Postage Type", max_length=2, choices=POSTAGE_TYPES)
	postage_rate = models.DecimalField(verbose_name = "Postage Rate", max_digits=6,decimal_places=2)
	postage_rate_max_items = models.PositiveSmallIntegerField(verbose_name="Maximum number of items for Postage Rate", default=5)
	postage_rate_per_extra_item = models.DecimalField(verbose_name = "Postage Rate per extra item", max_digits=6,decimal_places=2)
	date_created = models.DateTimeField(default=timezone.now)
	last_edited = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.get_postage_type_display()

class PostageType(models.Model):

	POSTAGE_TYPES = (
		('TK', 'Tracked'),
		('SD', 'Standard'),
	)

	class Meta:
		app_label = "shipping"

	postage_id = models.CharField(primary_key=True,verbose_name="Postage Type", max_length=2, choices=POSTAGE_TYPES)
	postage_short_desc = models.CharField(verbose_name="Short Description of Postage Type", max_length=255, blank=False)

	def __str__(self):
		return self.get_postage_id_display()