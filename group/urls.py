from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('refresh', views.refresh_groups, name='refresh_groups'),
]
