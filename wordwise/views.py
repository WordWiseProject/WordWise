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

from wordwise.forms import CollectionForm, FillInTheBlankForm, SelectDefinitionForm, TestForm
from wordwise.models import Definition, Example, TypeOf, UserData, Word, WordDeck

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))
HEADERS = {"X-RapidAPI-Key": env("X_RAPIDAPI_KEY"), "X-RapidAPI-Host": env("X_RAPIDAPI_HOST")}


def get_word(word: str):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/"
    try:
        word = Word.objects.get(vocab=word.lower())
    except Word.DoesNotExist:
        response = requests.get(url, headers=HEADERS)
        print(response.status_code)
        if response.status_code == 404:
            return None
        word_json = response.json()
        if "results" not in word_json:
            return None
        word = Word(vocab=word_json["word"].lower())
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
    word_list = list(type_json["hasTypes"])
    return word_list


class Home(View):
    def get(self, request):
        type_list = TypeOf.objects.all()
        random_type_list = random.sample(list(type_list), 8)
        context = {"type_of": random_type_list}
        return render(request, "wordwise/index.html", context)


class QuickFlashcardMode(View):
    def get(self, request, pk):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        word_list = get_list_word_from_type_of(pk)
        random.seed(request.session.get("random_seed"))
        try:
            random_word_list = random.sample(word_list, 10)
        except ValueError:
            random_word_list = random.sample(get_list_word_from_type_of(pk), len(word_list))
        for word in random_word_list:
            get_word(word=word)
        defi_list = list(
            Definition.objects.filter(type_of__type_of=pk).filter(word__vocab__in=random_word_list).distinct("word")
        )
        p = Paginator(defi_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        return render(request, "wordwise/flashcard.html", {"defi": defi})


class DeckFlashcardMode(View):
    def get(self, request, pk):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        word_list = list(Definition.objects.filter(collection__id=pk))
        if len(word_list) == 0:
            return redirect("wordwise:deck_detail", pk=pk)
        random.seed(request.session.get("random_seed"))
        random.shuffle(word_list)
        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        return render(request, "wordwise/flashcard.html", {"defi": defi, "pk": pk})


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
        if request.session.get("current_deck") != 0:
            request.session["current_deck"] = 0
        word_list = sorted(Definition.objects.filter(example__isnull=False), key=lambda x: random.random())
        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        return render(
            request,
            "wordwise/fill_in_blank.html",
            {"defi": defi, "form": FillInTheBlankForm, "current_deck": request.session.get("current_deck")},
        )

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
        return render(
            request,
            "wordwise/fill_in_blank.html",
            {"defi": defi, "form": FillInTheBlankForm, "current_deck": request.session.get("current_deck")},
        )

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


def delete_deck(request, pk):
    deck_id = pk
    deck = WordDeck.objects.get(id=deck_id)
    if request.user != deck.user:
        return redirect("wordwise:deck_index")
    deck.delete()
    return redirect("wordwise:deck_index")


# @login_required
class DeckCreateView(View):
    def get(self, request):
        return redirect("wordwise:deck_index")

    def post(self, request):
        form = CollectionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            desc = form.cleaned_data["description"]
            collection = WordDeck(name=name, description=desc, user=request.user)
            collection.save()
            return redirect("wordwise:deck_index")
        return redirect("wordwise:deck_index")


class DeckDetailView(View):
    def get(self, request, pk):
        request.session["current_deck"] = pk
        if request.session.get("random_seed"):
            request.session.pop("random_seed")
        template_name = "wordwise/deck_detail.html"
        deck = WordDeck.objects.get(pk=pk)
        return render(request, template_name=template_name, context={"deck": deck})

    def delete_word(self, pk, word_id):
        deck_id = pk
        deck = WordDeck.objects.get(id=deck_id)
        definition = Definition.objects.get(id=word_id)
        deck.definition_set.remove(definition)
        return redirect("wordwise:deck_detail", pk=pk)


class SearchWord(View):
    def post(self, request, pk):
        word = request.POST.get("word")
        print(word)
        word = get_word(word.strip())
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


class DeckTestMode(View):
    def get(self, request, pk):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        if request.session.get("current_deck") != pk:
            request.session["current_deck"] = pk
        word_list = list(Definition.objects.filter(collection__id=pk))
        if len(word_list) == 0:
            return redirect("wordwise:deck_detail", pk=pk)
        random.seed(request.session.get("random_seed"))
        random_definition_list = list(Definition.objects.all().order_by("?")[:3])
        random.shuffle(word_list)
        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        current_defi = defi.object_list[0]
        random_definition_list.append(current_defi)
        random.shuffle(random_definition_list)
        form = TestForm(definition=random_definition_list, current=current_defi.id)
        return render(request, "wordwise/test_mode.html", {"defi": defi, "current_deck": pk, "form": form})

    def post(self, request):
        answer = request.POST.get("definition")
        correct_defi = request.POST.get("current")
        next_page = int(request.POST.get("next_page_number"))
        has_next = bool(strtobool(request.POST.get("has_next")))
        current_deck = request.session.get("current_deck")
        current_defi = Definition.objects.get(id=correct_defi)
        contexts = {
            "next_page": next_page,
            "has_next": has_next,
            "correct_defi": current_defi,
            "current_deck": current_deck,
        }
        if not has_next:
            request.session.pop("random_seed")
        if answer == correct_defi:
            return render(request, "wordwise/test_pass.html", context=contexts)
        return render(request, "wordwise/test_fail.html", context=contexts)


class QuickTestMode(View):
    def get(self, request):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        if request.session.get("current_deck") != 0:
            request.session["current_deck"] = 0
        word_list = list(Definition.objects.all())
        random.seed(request.session.get("random_seed"))
        random_definition_list = list(Definition.objects.all().order_by("?")[:3])
        random.shuffle(word_list)
        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        current_defi = defi.object_list[0]
        random_definition_list.append(current_defi)
        random.shuffle(random_definition_list)
        form = TestForm(definition=random_definition_list, current=current_defi.id)
        return render(
            request,
            "wordwise/test_mode.html",
            {"defi": defi, "current_deck": request.session.get("current_deck"), "form": form},
        )

    def post(self, request):
        answer = request.POST.get("definition")
        correct_defi = request.POST.get("current")
        next_page = int(request.POST.get("next_page_number"))
        has_next = bool(strtobool(request.POST.get("has_next")))
        current_deck = request.session.get("current_deck")
        current_defi = Definition.objects.get(id=correct_defi)
        contexts = {
            "next_page": next_page,
            "has_next": has_next,
            "correct_defi": current_defi,
            "current_deck": current_deck,
        }
        if not has_next:
            request.session.pop("random_seed")
        if answer == correct_defi:
            return render(request, "wordwise/test_pass.html", context=contexts)
        return render(request, "wordwise/test_fail.html", context=contexts)
