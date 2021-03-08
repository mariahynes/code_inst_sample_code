from django.shortcuts import render
from accounts.models import User
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UserLoginForm
from django.contrib import messages
from django.conf import settings
from django.contrib import messages, auth
from django.template.context_processors import csrf
import carts.templatetags.cart_extras as cart_extras


def login(request):
	errors = []
	old_cart_id = ""
	old_cart_obj = []

	if request.method == 'POST':

		form = UserLoginForm(request.POST)
		if form.is_valid():	

			user = auth.authenticate(email=request.POST.get('email'),
									 password=request.POST.get('password'))

			if user is not None:

				#save the cart object (aka session id) if session has already been started
				the_session_id = request.COOKIES['sessionid']
				old_cart_id = cart_extras.get_cart_id(request)
				old_cart_obj = cart_extras.get_cart_object(request,old_cart_id)
				
				auth.login(request, user)
				
				if old_cart_obj:
					#save old cart_id and obj in session
					request.session['existing_cart_id'] = old_cart_id
					request.session['existing_cart_obj'] = old_cart_obj
					
				#check the 'next' value of the signin
				next_url = request.GET.get('next')
				if next_url:
					return HttpResponseRedirect(next_url)
				else:
					return HttpResponseRedirect('/')
				
			else:
				#print("not a valid user")
				errors.append("Your details were not recognised. Check your email and password.")
	else:
		
		form = UserLoginForm()

	args = {'form': form,
			'errors':errors}

	args.update(csrf(request))
	return render(request, 'login.html', args)