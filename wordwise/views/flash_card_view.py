import random

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views import View

from wordwise.models import Definition, MemoriseStatus, UserData

from .api_view import get_list_word_from_type_of, get_word

User = get_user_model()


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
            random_word_list = random.sample(word_list, 15)
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


class FlashCardProfile(View):
    def get(self, request, user_name, fav):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        fav_bool = fav.lower() in ["true", "1", "yes"]
        user = User.objects.get(username=user_name)
        if fav_bool:
            word_list = list(UserData.objects.get(user=user).favorite.all())
        else:
            memorise_status = MemoriseStatus.objects.filter(user=user)
            memorised_definitions = Definition.objects.filter(memorise__in=memorise_status).distinct()
            word_list = list(
                Definition.objects.filter(not_memorise__in=memorise_status)
                .exclude(id__in=memorised_definitions.values_list("id", flat=True))
                .distinct()
            )

        if len(word_list) == 0:
            return redirect("users:detail", user_name=user_name)
        random.seed(request.session.get("random_seed"))
        random.shuffle(word_list)

        if request.user.is_authenticated:
            fav_list = UserData.objects.get(user=request.user.id).favorite.all()
        else:
            fav_list = None

        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        return render(request, "wordwise/flashcard.html", {"defi": defi, "user_name": user_name, "fav_list": fav_list})
