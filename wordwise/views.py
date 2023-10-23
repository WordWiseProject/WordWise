from django.http.response import HttpResponse
from django.shortcuts import render


def home(request):
    return render(request, 'wordwise/index.html')


def flashcard_view(request):
    return render(request, 'wordwise/flashcard.html')
