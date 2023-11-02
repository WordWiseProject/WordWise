from django.db import models

from .definition import Definition


class Example(models.Model):
    """
    Example sentence for each definition.

    :param example: Example sentence.
    :type example: str
    :param example_of: The definition of this example.
    :type example_of: Definition
    """

    example = models.CharField(max_length=255)
    example_of = models.ForeignKey(Definition, on_delete=models.CASCADE)
