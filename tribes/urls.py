from django.urls import path
from . import views

urlpatterns = [
    path('explore/',         views.explore,         name='explore'),
    path('explore/events/',  views.explore_events,  name='explore_events'),
    path('onboarding/',      views.onboarding,      name='onboarding'),
    path('onboarding/save/', views.save_onboarding, name='save_onboarding'),
    path('join/<int:tribe_id>/', views.join_tribe,  name='join_tribe'),
]
