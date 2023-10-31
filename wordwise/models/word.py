from django.db import models

from .collection import Collection


class Word(models.Model):
    """
    A class representing vocabulary

    :param vocab: specific Vocabulary
    :type vocab: str
    :param collection: Collections that contain this vocabulary
    :type collection: Collection
    """

    vocab = models.CharField(max_length=255)
    collection = models.ManyToManyField(Collection)
