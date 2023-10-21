from django.db import models
from wordwise.users.models import User


class Collection(models.Model):
    """
    User's Word Collection

    :param name: Collection's name
    :type name: str
    :param user: Collection's owner
    :type name: User
    """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
