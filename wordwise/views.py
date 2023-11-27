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

from wordwise.forms import CollectionForm, FillInTheBlankForm, RandomFavoriteForm, SelectDefinitionForm, TestForm
from wordwise.models import Definition, Example, MemoriseStatus, TypeOf, UserData, Word, WordDeck

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
        pk = pk.lower()
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        try:
            word_list = get_list_word_from_type_of(pk)
        except KeyError:
            return redirect("wordwise:index")
        if len(word_list) == 0:
            return redirect("wordwise:index")
        random.seed(request.session.get("random_seed"))

        try:
            random_word_list = random.sample(word_list, 1000)
        except ValueError:
            random_word_list = random.sample(get_list_word_from_type_of(pk), len(word_list))
        for word in random_word_list:
            get_word(word=word)

        defi_list = list(
            Definition.objects.filter(type_of__type_of=pk).filter(word__vocab__in=random_word_list).distinct("word")
        )

        if not defi_list:
            return redirect("wordwise:index")

        if request.user.is_authenticated:
            fav_list = UserData.objects.get(user=request.user.id).favorite.all()
        else:
            fav_list = None

        p = Paginator(defi_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        return render(request, "wordwise/flashcard.html", {"defi": defi, "fav_list": fav_list})


class DeckFlashcardMode(View):
    def get(self, request, pk):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        word_list = list(Definition.objects.filter(collection__id=pk))
        if len(word_list) == 0:
            return redirect("wordwise:deck_detail", pk=pk)
        random.seed(request.session.get("random_seed"))
        random.shuffle(word_list)

        if request.user.is_authenticated:
            fav_list = UserData.objects.get(user=request.user.id).favorite.all()
        else:
            fav_list = None

        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        return render(request, "wordwise/flashcard.html", {"defi": defi, "pk": pk, "fav_list": fav_list})


class NotRememberFlashcardMode(View):
    def get(self, request, pk):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)

        memorise_status = MemoriseStatus.objects.get(user=request.user.id, deck__id=pk)
        word_list = list(memorise_status.not_memorise.all())

        if len(word_list) == 0:
            return redirect("wordwise:deck_detail", pk=pk)
        random.seed(request.session.get("random_seed"))
        random.shuffle(word_list)

        if request.user.is_authenticated:
            fav_list = UserData.objects.get(user=request.user.id).favorite.all()
        else:
            fav_list = None

        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        return render(request, "wordwise/flashcard.html", {"defi": defi, "pk": pk, "fav_list": fav_list})


def check_fill_in_the_blank_unauthorized(request, answer, current_defi, contexts):
    if answer.lower() == current_defi.word.vocab.lower():
        return render(request, "wordwise/fill_pass.html", context=contexts)
    return render(request, "wordwise/fill_fail.html", context=contexts)


def check_fill_in_the_blank_answer(request, quick: bool):
    answer = request.POST.get("answer")
    defi = request.POST.get("defi")
    next_page = int(request.POST.get("next_page_number"))
    has_next = bool(strtobool(request.POST.get("has_next")))
    current_deck = request.session.get("current_deck")
    current_defi = Definition.objects.filter(definition=defi).first()
    vocab = current_defi.word.vocab

    contexts = {"next_page": next_page, "has_next": has_next, "test2": vocab, "current_deck": current_deck}
    current_defi = Definition.objects.filter(definition=defi).first()

    if not request.user.is_authenticated:
        return check_fill_in_the_blank_unauthorized(request, answer, current_defi, contexts)

    if quick:
        status = MemoriseStatus.objects.get(user=request.user.id, deck__isnull=True)
    else:
        status = MemoriseStatus.objects.get(user=request.user.id, deck=current_deck)

    if not has_next:
        request.session.pop("random_seed")

    if answer.lower() == current_defi.word.vocab.lower():
        if current_defi in status.not_memorise.all():
            status.not_memorise.remvoe(current_defi)
        status.memorise.add(current_defi)
        return render(request, "wordwise/fill_pass.html", context=contexts)
    if current_defi in status.memorise.all():
        status.memorise.remove(current_defi)
    status.not_memorise.add(current_defi)
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
            "wordwise/quick_fill_in.html",
            {"defi": defi, "form": FillInTheBlankForm, "current_deck": request.session.get("current_deck")},
        )

    def post(self, request):
        return check_fill_in_the_blank_answer(request, quick=True)


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
        return check_fill_in_the_blank_answer(request, quick=False)


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
            collection = WordDeck(name=name, description=desc, user=request.user, private=True)
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
        print("is private", deck.private)

        if deck.private and deck.user != request.user:
            return redirect("wordwise:deck_index")

        if request.user.is_authenticated:
            try:
                status = MemoriseStatus.objects.get(user=request.user, deck=deck)
            except MemoriseStatus.DoesNotExist:
                status = MemoriseStatus.objects.create(user=request.user, deck=deck)
            memorise_status = MemoriseStatus.objects.get(user=request.user.id, deck__id=pk)
            memorised_definitions = memorise_status.memorise.all()
            not_memorised_definitions = memorise_status.not_memorise.all()
        else:
            status = None
            memorise_status = None
            memorised_definitions = None
            not_memorised_definitions = None
        print(memorised_definitions, not_memorised_definitions)

        return render(
            request,
            template_name=template_name,
            context={
                "deck": deck,
                "status": status,
                "memorised": memorised_definitions,
                "not_memorised": not_memorised_definitions,
            },
        )

    def delete_word(self, pk, word_id):
        deck = WordDeck.objects.get(id=pk)
        if deck.user != self.user:
            return redirect("wordwise:deck_detail", pk=pk)
        definition = Definition.objects.get(id=word_id)
        deck.definition_set.remove(definition)
        return redirect("wordwise:deck_detail", pk=pk)


class PrivateDeck(View):
    def get(self, request, pk):
        deck = WordDeck.objects.get(pk=pk)
        if deck.user != request.user:
            return redirect("wordwise:deck_index")
        context = {"deck_id": pk}
        if deck.private:
            return render(request, "wordwise/lock_deck.html", context)
        deck.private = True
        deck.save()
        print(deck.private)
        return render(request, "wordwise/lock_deck.html", context)


class UnPrivateDeck(View):
    def get(self, request, pk):
        deck = WordDeck.objects.get(pk=pk)
        if deck.user != request.user:
            return redirect("wordwise:deck_index")
        context = {"deck_id": pk}
        if not deck.private:
            return render(request, "wordwise/unlock_deck.html", context)
        deck.private = False
        deck.save()
        print(deck.private)
        return render(request, "wordwise/unlock_deck.html", context)


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


def check_test_ano(request, contexts, answer, correct_defi):
    if not contexts["has_next"]:
        request.session.pop("random_seed")
    if answer == correct_defi:
        # add to memorise word but check is in not memorise first
        return render(request, "wordwise/test_pass.html", context=contexts)
    return render(request, "wordwise/test_fail.html", context=contexts)


def check_test_mode(request, quick):
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
    if not request.user.is_authenticated:
        return check_test_ano(request, contexts, answer, correct_defi)
    if quick:
        status = MemoriseStatus.objects.get(user=request.user.id, deck__id=int(current_deck))
    else:
        status = MemoriseStatus.objects.get(user=request.user.id, deck__isnull=True)

    if not has_next:
        request.session.pop("random_seed")
    if answer == correct_defi:
        if current_defi in status.not_memorise.all():
            status.not_memorise.remove(current_defi)
        status.memorise.add(current_defi)
        return render(request, "wordwise/test_pass.html", context=contexts)
    if current_defi in status.memorise.all():
        status.memorise.remove(current_defi)
    status.not_memorise.add(current_defi)
    return render(request, "wordwise/test_fail.html", context=contexts)


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
        return check_test_mode(request, quick=False)


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
            "wordwise/quick_test_mode.html",
            {"defi": defi, "current_deck": request.session.get("current_deck"), "form": form},
        )

    def post(self, request):
        return check_test_mode(request, quick=True)


class AddToFavorite(View):
    def get(self, request, pk):
        definition = Definition.objects.get(pk=pk)
        user_data = UserData.objects.get(user=request.user.id)
        if definition in user_data.favorite.all():
            print("exist")
            pass
        else:
            user_data.favorite.add(definition)
            print("added", definition)
        print(user_data.favorite.all())
        return render(request, "wordwise/delete_to_fav.html", context={"defi": definition})


class DeleteInFavorite(View):
    def get(self, request, pk):
        definition = Definition.objects.get(pk=pk)
        user_data = UserData.objects.get(user=request.user.id)
        if definition in user_data.favorite.all():
            user_data.favorite.remove(definition)
            print("remove")
            pass
        else:
            print("added", definition)
        print(user_data.favorite.all())
        return render(request, "wordwise/add_to_fav.html", context={"defi": definition})


class DeleteFromFavoriteProfile(View):
    def get(self, request, pk):
        definition = Definition.objects.get(pk=pk)
        user_data = UserData.objects.get(user=request.user.id)
        if definition in user_data.favorite.all():
            user_data.favorite.remove(definition)
            print("remove")
        else:
            print("added", definition)
        print(user_data.favorite.all())
        return redirect("users:detail", username=request.user.username)


class GetRandomFavorite(View):
    def get(self, request, pk):
        user_data = UserData.objects.get(user=request.user.id).favorite.all()
        form = RandomFavoriteForm(fav_list=user_data)
        return render(request, "wordwise/fav_list.html", context={"form": form, "deck_id": pk})


class GetSearchFavorite(View):
    def post(self, request, pk):
        word = request.POST.get("word")
        def_list = Definition.objects.filter(userdata__user=request.user.id).filter(word__vocab__icontains=word)
        if not def_list:
            return render(request, "wordwise/definition_list.html", context={"status": "fail"})
        form = RandomFavoriteForm(fav_list=def_list)
        return render(request, "wordwise/fav_list.html", {"form": form, "deck_id": pk})
