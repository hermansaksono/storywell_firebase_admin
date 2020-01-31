from django.urls import path

from . import views

urlpatterns = [
    # ex: /view/<user_id>/<event>/<start_date_str>/<end_date_str>
    path('view/<str:user_id>/<str:event>/<str:start_date>/<str:end_date>/', views.view_logs, name='view_logs'),
    # ex: /view/<user_id>/<event>/<start_date_str>/<end_date_str>
    path('compare/<str:user_id>/<str:event1>/<str:event2>/<str:start_date>/<str:end_date>/',
         views.compare_logs, name='compare_logs'),
    # ex: /refresh/<user_id>/<date_string>
    path('refresh/<str:user_id>/', views.refresh_logs, name='refresh_logs'),
    # ex: /refresh/<user_id>/until/<date_string>
    path('refresh/<str:user_id>/until/<str:end_date_str>/', views.refresh_logs, name='refresh_logs'),
    # ex: /refresh/<user_id>/<date_string>
    path('refresh/<str:user_id>/<str:date_string>/', views.refresh_logs_on_date, name='refresh_logs_on_date'),
]
