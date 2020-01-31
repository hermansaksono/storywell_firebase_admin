from django.urls import path

from . import views

urlpatterns = [
    # ex: /refresh/<user_id>/<date_string>
    path('refresh/<str:user_id>/', views.refresh_logs, name='refresh_logs'),
    # ex: /refresh/<user_id>/until/<date_string>
    path('refresh/<str:user_id>/until/<str:end_date_str>/', views.refresh_logs, name='refresh_logs'),
    # ex: /refresh/<user_id>/<date_string>
    path('refresh/<str:user_id>/<str:date_string>/', views.refresh_logs_on_date, name='refresh_logs_on_date'),
]
