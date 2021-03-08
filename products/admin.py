from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Product


class ProductAdminForm(forms.ModelForm):
	
	product_long_description = forms.CharField(widget=CKEditorWidget())

	class Meta:
		model = Product
		fields = '__all__'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	
	form = ProductAdminForm

	fields = (('id'),
		('product_display_name','is_activated'),
		('product_description'),
		('product_long_description'),
		('product_price', 'product_price_currency'),
		('stock_manufactured'), 
		('max_per_cart'),
		('product_image_sirv_1', 'product_image_sirv_1_desc'),
		('product_image_sirv_2', 'product_image_sirv_2_desc'),
		('product_image_sirv_3', 'product_image_sirv_3_desc'),
		('product_image_sirv_4', 'product_image_sirv_4_desc'),
		('product_image_sirv_5', 'product_image_sirv_5_desc'),
		('product_image_1', 'product_image_1_desc'),
		('product_image_2', 'product_image_2_desc'),
		('product_image_3', 'product_image_3_desc'),
		('product_image_4', 'product_image_4_desc'),
		('date_created'),
		('last_edited'))
	readonly_fields = ('id','date_created', 'last_edited')
	list_display = ('id','product_display_name','stock_manufactured', 'date_created','last_edited', 'is_activated')
	ordering = ('product_display_name',)
	search_fields=('product_display_name',)
	list_filter=('product_display_name','date_created', 'last_edited', 'is_activated')








    