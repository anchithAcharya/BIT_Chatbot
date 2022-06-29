from django.shortcuts import render


def home(request):
	return render(request, 'home/home.html')

def parents(request):
	return render(request, 'parents/index.html')