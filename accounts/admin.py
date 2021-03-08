from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
	
	model = User
	
	fieldsets = (
		(None, {'fields':('email','password', 'last_login')}),
		('Additional Info', {'fields':(('first_name','last_name'), 'phone','date_joined', 'privacy_policy_check','privacy_policy_checked_date')}),
		('Permissions', {'fields':('is_active', 'is_staff','is_superuser','groups', 'user_permissions',)}),
	)
	
	add_fieldsets = (
		(None, {'fields': ('email', 'password1', 'password2'), 'classes': ('wide',)}),
	)
	
	list_display = ('email', 'last_name', 'first_name', 'is_staff', 'is_superuser', 'last_login')
	
	list_filter = ('is_staff', 'is_superuser')
	
	search_fields = ('email','last_name','first_name',)
	
	ordering = ('email','last_name','first_name',)
	
	filter_horizontal = ('groups', 'user_permissions')
	
	readonly_fields =  ('last_login','date_joined',)
