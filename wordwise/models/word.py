from django.db import models


class Word(models.Model):
    """
    A class representing vocabulary

    :param vocab: specific Vocabulary
    :type vocab: str
    """

    vocab = models.CharField(max_length=255)
