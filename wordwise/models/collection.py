from django.conf import settings
from django.db import models


class Collection(models.Model):
    """
    User's Word Collection

    :param name: Collection's name
    :type name: str
    :param user: Collection's owner
    :type name: User
    """

    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, null=True)
