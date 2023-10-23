from django.contrib.auth.models import User
from django.db import models


class UserData(models.Model):
    """
    A class representing User's data

    :param user: specific User
    :type user: User
    :param display_name: the User's display name
    :type display_name: str
    :param streak: Number of consecutive days using the app
    :type streak: int
    :param daily_percentage: Percentage of memorized words per day
    :type daily_percentage: float
    :param daily_total: Number of vocabulary words memorized per day
    :type daily_total: int
    """

    # pic
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    display_name = models.CharField(max_length=255)
    streak = models.IntegerField(default=0)
    daily_percentage = models.FloatField(default=0)
    daily_total = models.IntegerField(default=0)
