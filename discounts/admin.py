from django.contrib import admin
from .models import Discount
from products.models import Product

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):

	fields = (('discount_code'),
		('discount_type'),
		('discount_percentage'),
		('discount_desc'),
		('product_id'),
		('usage_frequency'),
		('used_by_order_id'),
		('valid_from'),
		('valid_until'),
		('date_created'),
		('last_edited'))
	readonly_fields = ('date_created', 'discount_desc','last_edited','used_by_order_id','is_active','is_available','is_expired')
	list_display = ('discount_code','discount_desc','is_active','is_available', 'is_expired', 'usage_frequency','valid_from','valid_until',)
	ordering = ('valid_from',)
	search_fields=('discount_code',)
	list_filter=('discount_code',)

