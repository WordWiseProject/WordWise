from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView

from wordwise.forms import CollectionForm, SelectDefinitionForm
from wordwise.models import Definition, MemoriseStatus, WordDeck

from .api_view import get_word


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
