from django.contrib import admin
from .models import CartDefault

@admin.register(CartDefault)
class CartDefaultAdmin(admin.ModelAdmin):

	fields = (('id'),
		('max_per_cart'),
		('date_created'),
		('last_edited'))
	readonly_fields = ('id','date_created', 'last_edited',)
	list_display = ('id','max_per_cart', 'date_created','last_edited')
	


	def has_add_permission(self, request):
		return False

    
	def has_delete_permission(self, request, obj=None):
		return False

'''
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

	fields = (('id'),
		('date_created'),
		('last_edited'))
	readonly_fields = ('date_created', 'last_edited',)
	list_display = ('id', 'date_created','last_edited')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

	fields = (('cart_ID'),
		('product_ID'),
		('product_quantity'),
		('discount_code'),
		('product_price_before_discount'),
		('product_price_after_discount'),
		('product_sub_total'),
		('date_added'),
		('last_edited'))
	readonly_fields = ('date_added', 'last_edited',)
	list_display = ('cart_ID','product_ID','product_quantity', 'product_price_after_discount','product_sub_total','date_added','last_edited')
	'''