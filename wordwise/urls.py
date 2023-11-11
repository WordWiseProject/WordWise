from django.contrib.auth.decorators import login_required
from django.shortcuts import reverse
from django.urls import path

from . import views

app_name = "wordwise"
urlpatterns = [
    path("", views.Home.as_view(), name="index"),
    path("flashcard.html", views.flashcard_view, name="flashcard"),
    # path("jeopardy.html", views.jeopardy_view, name="jeopardy"),
    path("flashcard.html/<type_of>", views.flashcard_view, name="flashcard"),
    path("fill", views.FillInTheBlank.as_view(), name="fill_in"),
    path("collection_index", views.CollectionIndexView.as_view(), name="collection_index"),
    path(
        "create_collection",
        login_required(views.CollectionCreateView.as_view(), login_url="google_login"),
        name="create_collection",
    ),
]
