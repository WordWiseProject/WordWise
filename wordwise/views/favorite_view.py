from django.shortcuts import redirect, render
from django.views import View

from wordwise.forms import RandomFavoriteForm
from wordwise.models import Definition, UserData


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
