from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = "wordwise"
urlpatterns = [
    path("", views.Home.as_view(), name="index"),
    path("flashcard/<pk>", views.QuickFlashcardMode.as_view(), name="flashcard"),
    path("flashcard_deck/<pk>", views.DeckFlashcardMode.as_view(), name="flashcard_deck"),
    path("fill", views.FillInTheBlank.as_view(), name="fill_in"),
    path("fill/<int:pk>", views.FillInTheBlankDeck.as_view(), name="fill_in_deck"),
    path("sup_fill", views.FillInTheBlankDeck.as_view(), name="sup_fill_in_deck"),
    path("deck_index", views.DeckIndexView.as_view(), name="deck_index"),
    path("delete_deck/<int:pk>", views.delete_deck, name="delete_deck"),
    path(
        "deck_collection",
        login_required(views.DeckCreateView.as_view(), login_url="google_login"),
        name="create_collection",
    ),
    path("deck/<int:pk>", views.DeckDetailView.as_view(), name="deck_detail"),
    path("search_word/<int:pk>", views.SearchWord.as_view(), name="search_word"),
    path("add_word_deck/<int:pk>", views.AddWordToDeck.as_view(), name="add_word_to_deck"),
    path("test_deck/<int:pk>", views.DeckTestMode.as_view(), name="test_deck"),
    path("test_deck", views.DeckTestMode.as_view(), name="submit_test_deck"),
    path("quick_test_deck", views.QuickTestMode.as_view(), name="quick_test_deck"),
    path("delete_word_deck/<int:pk>/<int:word_id>", views.DeckDetailView.delete_word, name="delete_word"),
    path("add_to_fav/<int:pk>", views.AddToFavorite.as_view(), name="add_to_fav"),
    path("delete_to_fav/<int:pk>", views.DeleteInFavorite.as_view(), name="delete_to_fav"),
    path("delete_to_fav_profile/<int:pk>", views.DeleteFromFavoriteProfile.as_view(), name="delete_from_fave_profile"),
    path("ran_fav/<int:pk>", views.GetRandomFavorite.as_view(), name="ran_fav"),
    path("search_fav/<int:pk>", views.GetSearchFavorite.as_view(), name="search_fav"),
    path("lock_deck/<int:pk>", views.PrivateDeck.as_view(), name="lock_deck"),
    path("unlock_deck/<int:pk>", views.UnPrivateDeck.as_view(), name="unlock_deck"),
]
