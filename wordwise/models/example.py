import re

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

    def censor(self) -> str:
        """Censor the root word."""
        vocab = self.example_of.word.vocab
        if (
            re.search(r"\b" + re.escape(vocab[:-1]) + r"ing\b", self.example)
            or re.search(r"\b" + re.escape(vocab[:-1]) + r"ed\b", self.example)
            or re.search(r"\b" + re.escape(vocab[:-1]) + r"le\b", self.example)
            or re.search(r"\b" + re.escape(vocab[:-1]) + r"able\b", self.example)
        ):
            censored_sentence = re.sub(
                re.escape(vocab[:-1]),
                "_" * len(vocab[:-1]),
                self.example,
                flags=re.IGNORECASE,
            )
        else:
            censored_sentence = re.sub(
                re.escape(vocab),
                "_" * len(vocab),
                self.example,
                flags=re.IGNORECASE,
            )
        return censored_sentence

    def __str__(self) -> str:
        return self.example
