from django.db import models

from .type_of import TypeOf
from .word import Word
from .worddeck import WordDeck


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
    :type collection: WordDeck
    """

    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    definition = models.CharField(max_length=255)
    part_of_speech = models.CharField(max_length=255, null=True)
    type_of = models.ManyToManyField(TypeOf)
    collection = models.ManyToManyField(WordDeck)

    def __str__(self):
        return self.word.vocab
