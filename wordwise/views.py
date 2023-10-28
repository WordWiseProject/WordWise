from pathlib import Path

import environ
import requests
from django.shortcuts import render

from .models import Definition, TypeOf, Word

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
env = environ.Env()

env.read_env(str(BASE_DIR / ".env"))

HEADERS = {"X-RapidAPI-Key": env("X_RAPIDAPI_KEY"), "X-RapidAPI-Host": env("X_RAPIDAPI_HOST")}


def get_word(word: str):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/"
    try:
        word = Word.objects.get(vocab=word)
    except Word.DoesNotExist:
        response = requests.get(url, headers=HEADERS)
        word_json = response.json()
        word = Word(vocab=word_json["word"])
        word.save()
        for results in word_json["results"]:
            defi = Definition(
                word=word,
                definition=results["definition"],
                part_of_speech=results["partOfSpeech"],
            )
            defi.save()
            for type_of in results["typeOf"]:
                try:
                    get_type_of = TypeOf.objects.get(type_of=type_of)
                    defi.type_of.add(get_type_of)
                except TypeOf.DoesNotExist:
                    get_type_of = TypeOf(type_of=type_of)
                    defi.type_of.add(get_type_of)

    return word


def home(request):
    return render(request, "wordwise/index.html")


def flashcard_view(request):
    return render(request, "wordwise/flashcard.html")
