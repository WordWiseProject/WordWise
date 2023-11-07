import random
from pathlib import Path

import environ
import requests
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View

from .forms import TestFrom, CollectionForm
from .models import Definition, Example, TypeOf, Word, Collection

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))
HEADERS = {"X-RapidAPI-Key": env("X_RAPIDAPI_KEY"), "X-RapidAPI-Host": env("X_RAPIDAPI_HOST")}


def get_word(word: str):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/"
    try:
        word = Word.objects.get(vocab=word)
        print(word)
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
            if "typeOf" in results:
                for type_of in results["typeOf"]:
                    try:
                        get_type_of = TypeOf.objects.get(type_of=type_of)
                        defi.type_of.add(get_type_of)
                    except TypeOf.DoesNotExist:
                        get_type_of = TypeOf(type_of=type_of)
                        get_type_of.save()
                        defi.type_of.add(get_type_of)
            if "examples" in results:
                for example in results["examples"]:
                    example_sentence = Example(example=example, example_of=defi)
                    example_sentence.save()

    return word


def get_list_word_from_type_of(type):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{type}/hasTypes"
    response = requests.get(url, headers=HEADERS)
    type_json = response.json()
    return list(type_json["hasTypes"])


class home(View):
    def get(self, request):
        context = {"type_of": ["business", "sport", "technology", "study"]}
        return render(request, "wordwise/index.html", context)

    def post(self, request):
        name = request.POST.get("name")
        desc = request.POST.get("desc")
        try:
            collection = Collection.objects.get(name=name)
        except Collection.DoesNotExist:
            user = request.user
            collection = Collection(name=name, user=user, desc=desc)
            # collection.save()
        form = CollectionForm()
        return render(request, 'wordwise/index.html', {'form': form})


def flashcard_view(request, type_of):
    all_word_list = get_list_word_from_type_of(type_of)
    random_word_list = random.sample(all_word_list, 10)
    for word in random_word_list:
        get_word(word=word)
    word_list = list(Definition.objects.filter(type_of__type_of=type_of).filter(word__vocab__in=random_word_list))
    context = {"word_list": word_list}
    return render(request, "wordwise/flashcard.html", context)


def jeopardy_view(request):
    return render(request, "wordwise/jeopardy.html")


class FillInTheBlank(View):
    def get(self, request):
        word_list = sorted(Definition.objects.filter(example__isnull=False), key=lambda x: random.random())
        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        return render(request, "wordwise/fill_in_blank.html", {"defi": defi, "form": TestFrom})

    def post(self, request):
        answer = request.POST.get("answer")
        defi = request.POST.get("defi")
        current_defi = Definition.objects.filter(definition=defi).first()

        if answer == current_defi.word.vocab:
            print("yes")
            return render(request, "wordwise/fill_pass.html", context={"test2": current_defi.word.vocab})
        print("no")
        return render(request, "wordwise/fill_fail.html", context={"test2": current_defi.word.vocab})


class Collection(View):
    def add_word(self):
        pass

    def delete_word(self):
        pass
