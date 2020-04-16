from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    app_start_date = models.DateTimeField()
    last_update = models.DateTimeField(default=0)
    is_visible = models.BooleanField(default=False)

    def __str__(self):
        return self.user_id


    def get_members(self) -> list:
        return list(Person.objects.filter(user=self))


class Person(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    person_id = models.IntegerField()
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20)

    def __str__(self):
        return self.name
