from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="index"),
    path("flashcard.html", views.flashcard_view, name="flashcard"),
    path("jeopardy.html", views.jeopardy_view, name="jeopardy"),
    path("flashcard.html/<type_of>", views.flashcard_view, name="flashcard"),
]
