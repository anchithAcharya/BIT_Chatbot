from api import admin as admin_api
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm

def admin(request):
	if request.COOKIES.get('token'):
		return redirect('dashboard')

	else:
		return redirect('login')

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			response, status_code, cookies = admin_api.login(request.POST.get('id'), request.POST.get('password'))
			if status_code == 200:
				ret = redirect('dashboard')

				for cookie in cookies:
					if cookie.name == 'token':
						ret.set_cookie(cookie.name, cookie.value, expires=cookie.expires)

				return ret

			elif status_code == 401:
				messages.error(request, response.get('password', 'Authentication failed.'))
				ret = redirect('login')
				ret.cookies['form_id'] = form.cleaned_data.get('id')
				ret.cookies['password'] = form.cleaned_data.get('password')
				return ret

			elif status_code == 404:
				messages.error(request, response.get('id', 'User with given id/email not found.'))
				ret = redirect('login')
				ret.cookies['form_id'] = form.cleaned_data.get('id')
				ret.cookies['form_password'] = form.cleaned_data.get('password')
				return ret

			elif status_code == 400:
				for field in response:
					messages.error(request, response[field])

				return redirect('login')

		else:
			for field in form.errors:
				messages.error(request, form.errors[field])

			return redirect('login')

	else:
		params = {'form': LoginForm({
			'id': request.COOKIES.get('form_id'),
			'password': request.COOKIES.get('form_password')
		})}

		request.COOKIES.pop('form_id')
		request.COOKIES.pop('form_password')

		return render(request, 'admin/login.html', params)

def logout(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You are not logged in.')
		return redirect('login')

	response, status_code = admin_api.logout(request.COOKIES.get('token'))

	if status_code == 200:
		messages.success(request, response.get('success', 'Logout successful.'))
		request.COOKIES.pop('token')
		return redirect('home')

	elif status_code == 401:
		messages.error(request, response.get('detail', 'Authentication failed.'))
		return redirect('home')

def dashboard(request):
	if not request.COOKIES.get('token'):
		messages.error(request, 'You must be logged in to view the dashboard.')
		return redirect('login')

	page_no = request.GET.get('page', 1)
	response, status_code = admin_api.get_all_students(request.COOKIES.get('token'), page_no)
	
	if status_code == 200:
		response['total_pages'] = range(1, response['total_pages'] + 1)
		return render(request, 'admin/dashboard.html', response)

	else:
		if status_code == 404:
			messages.error(request, f"Invalid or empty page: {page_no}")
			return redirect('dashboard')

		elif status_code == 401:
			if request.META.get('HTTP_REFERER') is None:
				messages.error(request, 'Authentication error: ' + response.get('detail', 'Authentication failed.'))

			return redirect('login') 