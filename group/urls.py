from django.urls import path

from . import views

urlpatterns = [
    # ex: /refresh/
    path('refresh', views.refresh_groups, name='refresh_groups'),
]
