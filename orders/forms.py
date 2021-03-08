from django.forms import ModelForm,Textarea, TextInput
from .models import Order
from shipping.models import PostageRate
from discounts.models import Discount

class ShippingAddressForm(ModelForm):

	class Meta:
		model = Order
		fields = ['shipping_name',
		'shipping_address_line1',
		'shipping_address_line2',
		'shipping_address_city',
		'shipping_address_state',
		'shipping_address_postal_code',
		'shipping_address_country']
		widgets={
            'shipping_name':Textarea(attrs={'cols':50, 'rows':1}),
   			'shipping_address_line1':Textarea(attrs={'cols':50, 'rows':1}),
            'shipping_address_line2':Textarea(attrs={'cols':50, 'rows':1}),
        }
		

class CustomerNotesForm(ModelForm):

	class Meta:
		model = Order
		fields = ['customer_notes']
		widgets={
            'customer_notes':Textarea(attrs={'cols':50, 'rows':5, 'placeholder':'(Optional) Please add any delivery instructions, or notes on your order, here'}),
        }


class DiscountCodeForm(ModelForm):
	#'discount_desc':TextInput(attrs={'cols':8, 'rows':1,'readonly': 'readonly', 'required': False}),

	class Meta:
		model = Discount
		fields = ['discount_code']
		
		widgets={
            'discount_code':Textarea(attrs={'cols':8, 'rows':1, 'placeholder':'Type your Code here'}),
        }

class PostageTypeForm(ModelForm):

	class Meta:
		model = PostageRate
		fields = ['postage_type']
		
