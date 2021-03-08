"""shadydog_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from accounts import views as accounts_views
from django.contrib.auth import views as auth_views
import shop.templatetags.global_extras as global_extras

site_name = global_extras.return_site_name()
admin.site.site_header = site_name
admin.site.site_title = site_name
admin.site.index_title = site_name + " Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset',),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done',),
    path('admin/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm',),
    path('admin/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete',),
    path('admin/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change',),
    path('admin/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done',),
    path('', include('shop.urls')),
    path('', include('products.urls')),
    path('', include('carts.urls')),
    path('login/', accounts_views.login, name='login'),
    path('', include('django.contrib.auth.urls')),
]
