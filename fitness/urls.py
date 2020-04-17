from django.urls import path

from . import views

urlpatterns = [
    # ex: /all
    path('all', views.get_all_families, name='get_all_families'),
    # ex: /edit/<geostory_id>
    path('daily/<str:family_id>', views.get_family_daily_fitness, name="get_family_daily_fitness"),
    # ex: /sync/<family_id>
    path('sync/<str:family_id>', views.do_request_fitness_sync, name='do_request_fitness_sync'),

    # ex: /averages
    path('averages', views.get_caregiver_averages, name='get_caregiver_averages'),

]