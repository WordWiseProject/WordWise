import random
from distutils.util import strtobool
from pathlib import Path

import environ
import requests
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView

from wordwise.forms import CollectionForm, SelectDefinitionForm, TestFrom
from wordwise.models import Definition, Example, TypeOf, UserData, Word, WordDeck

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
        print(response.status_code)
        if response.status_code == 404:
            return None
        word_json = response.json()
        if "results" not in word_json:
            return None
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


class Home(View):
    def get(self, request):
        type_list = TypeOf.objects.all()
        random_type_list = random.sample(list(type_list), 7)
        context = {"type_of": random_type_list}
        print(random_type_list)
        return render(request, "wordwise/index.html", context)


def flashcard_view(request, pk):
    try:
        int(pk)
    except ValueError:
        all_word_list = get_list_word_from_type_of(pk)
        random_word_list = random.sample(all_word_list, 10)
        for word in random_word_list:
            get_word(word=word)
        word_list = list(Definition.objects.filter(type_of__type_of=pk).filter(word__vocab__in=random_word_list))
    else:
        all_word_list = WordDeck.objects.get(id=pk).definition_set.all()
        word_list = list(all_word_list)
        random.shuffle(word_list)
    context = {"word_list": word_list}
    return render(request, "wordwise/flashcard.html", context)


def jeopardy_view(request):
    return render(request, "wordwise/jeopardy.html")


def check_fill_in_the_blank_answer(request):
    answer = request.POST.get("answer")
    defi = request.POST.get("defi")
    next_page = int(request.POST.get("next_page_number"))
    has_next = bool(strtobool(request.POST.get("has_next")))
    current_deck = request.session.get("current_deck")
    current_defi = Definition.objects.filter(definition=defi).first()
    vocab = current_defi.word.vocab

    contexts = {"next_page": next_page, "has_next": has_next, "test2": vocab, "current_deck": current_deck}
    current_defi = Definition.objects.filter(definition=defi).first()

    if not has_next:
        request.session.pop("random_seed")
    if answer.lower() == current_defi.word.vocab.lower():
        return render(request, "wordwise/fill_pass.html", context=contexts)
    return render(request, "wordwise/fill_fail.html", context=contexts)


class FillInTheBlank(View):
    def get(self, request):
        word_list = sorted(Definition.objects.filter(example__isnull=False), key=lambda x: random.random())
        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        return render(request, "wordwise/fill_in_blank.html", {"defi": defi, "form": TestFrom})

    def post(self, request):
        return check_fill_in_the_blank_answer(request)


class FillInTheBlankDeck(View):
    def get(self, request, pk):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        if request.session.get("current_deck") != pk:
            request.session["current_deck"] = pk
        word_list = list(Definition.objects.filter(collection__id=pk).exclude(example__isnull=True))
        if len(word_list) == 0:
            return redirect("wordwise:deck_detail", pk=pk)
        random.seed(request.session.get("random_seed"))
        random.shuffle(word_list)
        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        return render(request, "wordwise/fill_in_blank.html", {"defi": defi, "form": TestFrom})

    def post(self, request):
        return check_fill_in_the_blank_answer(request)


class DeckIndexView(ListView):
    """Class based View for Index."""

    template_name = "wordwise/deck_index.html"
    context_object_name = "collections"

    def get_queryset(self):
        """Return all the user's collection"""
        return WordDeck.objects.filter(user=self.request.user.id)  # user's collection

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["others"] = WordDeck.objects.filter(~Q(user=self.request.user.id))  # other's collection
        context["form"] = CollectionForm()
        return context


# @login_required
class DeckCreateView(View):
    def get(self, request):
        return redirect("wordwise:collection_index")

    def post(self, request):
        form = CollectionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            desc = form.cleaned_data["description"]
            collection = WordDeck(name=name, description=desc, user=request.user)
            collection.save()
            return redirect("wordwise:collection_index")
        return redirect("wordwise:collection_index")


class DeckDetailView(View):
    def get(self, request, pk):
        request.session["current_deck"] = pk
        template_name = "wordwise/deck_detail.html"
        deck = WordDeck.objects.get(pk=pk)
        return render(request, template_name=template_name, context={"deck": deck})


class SearchWord(View):
    def post(self, request, pk):
        word = request.POST.get("word")
        print(word)
        word = get_word(word)
        if word is None:
            return render(request, "wordwise/definition_list.html", context={"status": "fail"})
        form = SelectDefinitionForm(word=word)
        return render(
            request, "wordwise/definition_list.html", context={"status": "success", "form": form, "deck_id": pk}
        )


class AddWordToDeck(View):
    def post(self, request, pk):
        definition_id = request.POST.get("definition")
        deck_id = pk
        definition = Definition.objects.get(id=definition_id)
        deck = WordDeck.objects.get(id=deck_id)
        deck.definition_set.add(definition)
        return redirect("wordwise:deck_detail", pk=pk)
