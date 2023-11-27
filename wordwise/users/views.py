from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

from wordwise.models import Definition, MemoriseStatus, UserData

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["fav_list"] = UserData.objects.get(user=self.object).favorite.all()
        except UserData.DoesNotExist:
            UserData.objects.create(user=self.object)
        memorise_status = MemoriseStatus.objects.filter(user=self.object)
        memorised_definitions = Definition.objects.filter(memorise__in=memorise_status).distinct()
        not_memorised_definitions = Definition.objects.filter(not_memorise__in=memorise_status).distinct()
        context["memorised"] = memorised_definitions
        context["not_memorised"] = not_memorised_definitions
        return context


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
