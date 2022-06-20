from django.shortcuts import render

from admin.views import admin

def home(request):
	return render(request, 'home/home.html')

def student(request):
	return render(request, 'student/index.html')

def staff(request):
	return render(request, 'staff/index.html')

def parents(request):
	return render(request, 'parents/index.html')