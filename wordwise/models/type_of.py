from django.db import models


class TypeOf(models.Model):
    """
    Definition of specific vocabulary

    :param type_of: Type of the vocabulary
    :type type_of: str
    """

    type_of = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.type_of
