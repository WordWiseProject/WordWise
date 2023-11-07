from django.urls import path

from . import views

app_name = "wordwise"
urlpatterns = [
    path("", views.home.as_view(), name="index"),
    path("flashcard.html", views.flashcard_view, name="flashcard"),
    path("jeopardy.html", views.jeopardy_view, name="jeopardy"),
    path("flashcard.html/<type_of>", views.flashcard_view, name="flashcard"),
    path("fill", views.FillInTheBlank.as_view(), name="fill_in"),
]
