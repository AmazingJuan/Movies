from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html', {'name': 'Juan Pablo de Jesús Avendaño Bustamante'} )

def about(request):
    return HttpResponse("<h1> Welcome to About Page</h1>")
