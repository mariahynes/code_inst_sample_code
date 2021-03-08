from django.urls import path
from . import views

urlpatterns = [

	path('show_product/<int:product_id>/', views.show_product, name='show_product'), 
	path('show_product/<int:product_id>/<int:quantity>/', views.show_product, name='show_product'), 
	
]