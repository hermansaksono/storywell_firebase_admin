from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('refresh/<str:user_id>/<str:date_string>/', views.refresh_logs, name='refresh_logs'),
]
