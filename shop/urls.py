from django.urls import path
from . import views

urlpatterns = [

	path('', views.index, name='index'),
	path('stripe_config/', views.stripe_config), 
	path('facebook_config/', views.facebook_config),
	path('success/', views.shop_success, name="payment_success"),
	path('cancelled/', views.shop_cancelled, name="payment_cancelled"),
]