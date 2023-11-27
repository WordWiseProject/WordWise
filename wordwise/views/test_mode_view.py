import random
from distutils.util import strtobool

from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views import View

from wordwise.forms import TestForm
from wordwise.models import Definition, MemoriseStatus


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
        status = MemoriseStatus.objects.get(user=request.user.id, deck__isnull=True)
    else:
        status = MemoriseStatus.objects.get(user=request.user.id, deck__id=int(current_deck))

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


class DeckNotMemoriseTestMode(View):
    def get(self, request, pk):
        if not request.session.get("random_seed", False):
            request.session["random_seed"] = random.randint(1, 10000)
        if request.session.get("current_deck") != pk:
            request.session["current_deck"] = pk
        word_list = list(MemoriseStatus.objects.get(user=request.user, deck=pk).not_memorise.all())
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
