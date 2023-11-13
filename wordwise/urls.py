from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = "wordwise"
urlpatterns = [
    path("", views.Home.as_view(), name="index"),
    path("flashcard.html", views.flashcard_view, name="flashcard"),
    # path("jeopardy.html", views.jeopardy_view, name="jeopardy"),
    path("flashcard/<pk>", views.flashcard_view, name="flashcard"),
    path("fill", views.FillInTheBlank.as_view(), name="fill_in"),
    path("fill/<int:pk>", views.FillInTheBlankDeck.as_view(), name="fill_in_deck"),
    path("deck_index", views.DeckIndexView.as_view(), name="deck_index"),
    path(
        "deck_collection",
        login_required(views.DeckCreateView.as_view(), login_url="google_login"),
        name="create_collection",
    ),
    path("deck/<int:pk>", views.DeckDetailView.as_view(), name="deck_detail"),
    path("search_word/<int:pk>", views.SearchWord.as_view(), name="search_word"),
    path("add_word_deck/<int:pk>", views.AddWordToDeck.as_view(), name="add_word_to_deck"),
]
