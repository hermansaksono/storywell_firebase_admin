from django.urls import path

from . import views

urlpatterns = [
    # ex: /all
    path('all', views.get_all_geostory, name='get_all_geostory'),
    # ex: /edit/<geostory_id>
    path('edit/<str:geostory_id>', views.GeoStoryUpdateView.as_view()),
]