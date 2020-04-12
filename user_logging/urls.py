from django.urls import path

from . import views
from eventlog import views as eventlog_views

urlpatterns = [
    # ex: /all
    path('all', views.get_all_families, name='get_all_families'),
    # ex: /refresh/<user_id>
    path('refresh/<str:family_id>', views.RefreshLogView.as_view()),
    # ex: /range/<user_id>
    path('range/<str:family_id>', views.SelectDateRangeForLogView.as_view()),
    # ex: /edit/<geostory_id>
    # path('daily/<str:family_id>', views.get_family_daily_fitness, name="get_family_daily_fitness"),

    # ex: /emotions/<user_id>/<start_date_str>/<end_date_str>/
    path('emotions/<str:user_id>/<str:start_date_str>/<str:end_date_str>',
         views.PrintableLogView.as_view()),
    path('emotions/<str:user_id>/<str:start_date_str>/<str:end_date_str>/<str:show_data>',
         views.PrintableLogView.as_view()),
]