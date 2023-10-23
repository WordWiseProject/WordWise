from django.db import models

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
    :param category: Category of the vocabulary
    :type category: str
    """

    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    definition = models.CharField(max_length=255)
    part_of_speech = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
