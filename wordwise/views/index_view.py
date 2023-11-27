import random

from django.shortcuts import render
from django.views import View

from wordwise.models import TypeOf


class Home(View):
    def get(self, request):
        type_list = TypeOf.objects.all()
        random_type_list = random.sample(list(type_list), 8)
        context = {"type_of": random_type_list}
        return render(request, "wordwise/index.html", context)
