from .api_view import get_list_word_from_type_of, get_word
from .deck_view import (
    AddWordToDeck,
    DeckCreateView,
    DeckDetailView,
    DeckIndexView,
    PrivateDeck,
    SearchWord,
    UnPrivateDeck,
    delete_deck,
)
from .favorite_view import (
    AddToFavorite,
    DeleteFromFavoriteProfile,
    DeleteInFavorite,
    GetRandomFavorite,
    GetSearchFavorite,
)
from .fill_in_the_blank_view import (
    FillInBlankProfile,
    FillInTheBlank,
    FillInTheBlankDeck,
    FillInTheBlankDeckNotMemorise,
)
from .flash_card_view import DeckFlashcardMode, FlashCardProfile, NotRememberFlashcardMode, QuickFlashcardMode
from .index_view import Home
from .test_mode_view import DeckNotMemoriseTestMode, DeckTestMode, QuickTestMode, TestModeProfile
