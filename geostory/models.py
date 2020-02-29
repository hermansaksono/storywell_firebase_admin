from django.db import models

# Create your models here.

class Geostory(models.Model):
    is_reviewed = models.BooleanField()
    story_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    last_update_timestamp = models.IntegerField()


