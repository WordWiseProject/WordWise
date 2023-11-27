import random
from distutils.util import strtobool

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views import View

from wordwise.forms import FillInTheBlankForm
from wordwise.models import Definition, MemoriseStatus, UserData

User = get_user_model()


def check_fill_in_the_blank_unauthorized(request, answer, current_defi, contexts):
    if answer.lower() == current_defi.word.vocab.lower():
        return render(request, "wordwise/fill_pass.html", context=contexts)
    return render(request, "wordwise/fill_fail.html", context=contexts)


def check_in_the_blank_profile(request, answer, current_defi, contexts):
    memorise_statuses = MemoriseStatus.objects.filter(user=request.user)
    all_mem = MemoriseStatus.objects.get(user=request.user, deck__isnull=True)
    contexts["user_name"] = request.user.username
    if answer.lower() == current_defi.word.vocab.lower():
        for status in memorise_statuses:
            if current_defi in status.not_memorise.all():
                status.not_memorise.remove(current_defi)
                status.memorise.add(current_defi)
        all_mem.memorise.add(current_defi)
        return render(request, "wordwise/fill_pass.html", context=contexts)
    for status in memorise_statuses:
        if current_defi in status.memorise.all():
            status.memorise.remove(current_defi)
            status.not_memorise.add(current_defi)
        all_mem.not_memorise.add(current_defi)
    return render(request, "wordwise/fill_fail.html", context=contexts)


def check_fill_in_the_blank_answer(request, quick: bool, profile: bool = False):
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

    if not request.user.is_authenticated:
        return check_fill_in_the_blank_unauthorized(request, answer, current_defi, contexts)

    print(profile)
    if profile:
        print("profile")
        return check_in_the_blank_profile(request, answer, current_defi, contexts)

    if quick:
        status = MemoriseStatus.objects.get(user=request.user.id, deck__isnull=True)
    else:
        status = MemoriseStatus.objects.get(user=request.user.id, deck=current_deck)

    if answer.lower() == current_defi.word.vocab.lower():
        if current_defi in status.not_memorise.all():
            status.not_memorise.remove(current_defi)
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


class FillInTheBlankDeckNotMemorise(View):
    def get(self, request, pk):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        if request.session.get("current_deck") != pk:
            request.session["current_deck"] = pk
        word_list = list(
            MemoriseStatus.objects.get(user=request.user, deck=pk).not_memorise.all().exclude(example__isnull=True)
        )
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


class FillInBlankProfile(View):
    def get(self, request, user_name, fav):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        user = User.objects.get(username=user_name)
        fav_bool = fav.lower() in ["true", "1", "yes"]

        if fav_bool:
            word_list = list(UserData.objects.get(user=user).favorite.all().exclude(example__isnull=True))
        else:
            memorise_status = MemoriseStatus.objects.filter(user=user)
            memorised_definitions = Definition.objects.filter(memorise__in=memorise_status).distinct()
            word_list = list(
                Definition.objects.filter(not_memorise__in=memorise_status)
                .exclude(id__in=memorised_definitions.values_list("id", flat=True))
                .exclude(example__isnull=True)
                .distinct()
            )

        if len(word_list) == 0:
            return redirect("users:detail", username=user_name)
        random.seed(request.session.get("random_seed"))
        random.shuffle(word_list)
        p = Paginator(word_list, 1)
        page = request.GET.get("page")
        defi = p.get_page(page)
        print(defi.object_list[0].word.vocab)
        return render(
            request,
            "wordwise/fill_in_blank.html",
            {"defi": defi, "form": FillInTheBlankForm, "user_name": user_name, "current_deck": 0},
        )

    def post(self, request):
        return check_fill_in_the_blank_answer(request, quick=False, profile=True)
