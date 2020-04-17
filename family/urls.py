from django.urls import path

from . import views

urlpatterns = [
    # ex: /all
    path('all', views.get_all_families, name='get_all_families'),

    # ex: /refresh
    path('refresh', views.refresh_families, name='refresh_families'),

    # ex: /edit/setting/<family_id>
    path('edit/setting/<str:family_id>', views.FamilyUpdateSetting.as_view()),
]