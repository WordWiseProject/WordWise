from django.db import models

from .collection import Collection
from .type_of import TypeOf
from .word import Word


class Definition(models.Model):
    """
    Definition of specific vocabulary

    :param word: Specific vocabulary
    :type word: Word
    :param definition: Definition of the vocabulary
    :type definition: str
    :param part_of_speech: Part of speech
    :type part_of_speech: str
    :param type_of: Category of the vocabulary
    :type type_of: str
    :param collection: Collections that contain this vocabulary
    :type collection: Collection
    """

    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    definition = models.CharField(max_length=255)
    part_of_speech = models.CharField(max_length=255, null=True)
    type_of = models.ManyToManyField(TypeOf)
    collection = models.ManyToManyField(Collection)
