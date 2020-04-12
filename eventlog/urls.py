from django.urls import path

from . import views

urlpatterns = [
    # ex: /view/<user_id>/<event>/<start_date_str>/<end_date_str>/daily
    path('view/<str:user_id>/<str:event>/<str:start_date>/<str:end_date>/daily',
         views.view_logs, name='view_logs'),
    # ex: /compare/<user_id>/<event>/<start_date_str>/<end_date_str>
    path('compare/<str:user_id>/<str:event1>/<str:event2>/<str:start_date>/<str:end_date>/daily',
         views.compare_logs, name='compare_logs'),

    # ex: /compare/<user_id>/<event>/<start_date_str>/<end_date_str>/weekly/<num_weeks>
    path('compare/<str:user_id>/<str:event1>/<str:event2>/<str:start_date>/<str:end_date>/weekly/<int:num_months>',
         views.compare_logs, name='compare_logs'),

    # ex: /refresh/<user_id>/<date_string>
    path('refresh/<str:user_id>/', views.refresh_logs, name='refresh_logs'),
    # ex: /refresh/<user_id>/until/<date_string>
    path('refresh/<str:user_id>/until/<str:end_date_str>/',
         views.refresh_logs, name='refresh_logs'),
    # ex: /refresh/<user_id>/<date_string>
    path('refresh/<str:user_id>/<str:date_string>/',
         views.refresh_logs_on_date, name='refresh_logs_on_date'),
]
