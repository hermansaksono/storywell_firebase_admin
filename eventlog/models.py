from django.db import models

from group.models import User


class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.CharField(max_length=100)
    date = models.DateField()
    count = models.IntegerField()

    unique_together = [['user', 'event', 'date']]
