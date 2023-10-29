from pathlib import Path

import environ
import requests
from django.shortcuts import render

from .models import Definition, TypeOf, Word

import random

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
                    get_type_of.save()
                    defi.type_of.add(get_type_of)
    return word


def get_word_from_type_of(type):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{type}/hasTypes"
    response = requests.get(url, headers=HEADERS)
    type_json = response.json()
    for results in type_json["hasTypes"]:
        get_word(word=results)
    word_list = list(Definition.objects.filter(type_of__type_of=type))
    ran_word_list = random.sample(word_list, 10)
    return ran_word_list


def home(request):
    context = {'type_of': ['business', 'sport', 'technology', 'study']}
    return render(request, "wordwise/index.html", context)


def flashcard_view(request, type_of):
    word_list = get_word_from_type_of(type_of)
    context = {'word_list': word_list}
    return render(request, "wordwise/flashcard.html", context)


def jeopardy_view(request):
    return render(request, "wordwise/jeopardy.html")
