from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    app_start_date = models.DateTimeField()
    last_update = models.DateTimeField(default=0)

    def __str__(self):
        return self.user_id
