from django.urls import path

from . import views
from eventlog import views as eventlog_views

urlpatterns = [
    # ex: /all
    path('all', views.get_all_families, name='get_all_families'),
    # ex: /range/<user_id>
    path('range/<str:family_id>', views.select_date_range_for_logs, name='select_date_range_for_logs'),
    # ex: /edit/<geostory_id>
    # path('daily/<str:family_id>', views.get_family_daily_fitness, name="get_family_daily_fitness"),

    # ex: /emotions/<user_id>/<start_date_str>/<end_date_str>/
    path('emotions/<str:user_id>/<str:start_date_str>/<str:end_date_str>', eventlog_views.view_moods, name='view_moods'),
]