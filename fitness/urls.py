from django.urls import path

from . import views

urlpatterns = [
    # ex: /all
    path('all', views.get_all_families, name='get_all_families'),
    # ex: /edit/<geostory_id>
    path('daily/<str:family_id>', views.get_family_daily_fitness, name="get_family_daily_fitness"),
]