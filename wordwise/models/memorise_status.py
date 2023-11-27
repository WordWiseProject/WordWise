from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.dispatch import receiver

from .definition import Definition, WordDeck

User = get_user_model()


class MemoriseStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deck = models.ForeignKey(WordDeck, on_delete=models.CASCADE, null=True, blank=True)
    memorise = models.ManyToManyField(Definition, related_name="memorise")
    not_memorise = models.ManyToManyField(Definition, related_name="not_memorise")


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    try:
        MemoriseStatus.objects.get(user=user, deck__isnull=True)
        print("exist")
    except MemoriseStatus.DoesNotExist:
        MemoriseStatus.objects.create(user=user, deck=None)
        print("not_exist")
