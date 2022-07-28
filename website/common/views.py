from django.shortcuts import render


def home(request):
	return render(request, 'home/home.html')

def chatbot(request):
	return render(request, 'home/chatbot.html', {'token': request.COOKIES.get('token')})