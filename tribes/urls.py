from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('explore/',         views.explore,         name='explore'),
    path('explore/events/',  views.explore_events,  name='explore_events'),

    # Auth-required user pages
    path('my/tribes/',       views.my_tribes,        name='my_tribes'),
    path('my/events/',       views.my_events,        name='my_events'),
    path('my/profile/',      views.my_profile,       name='my_profile'),

    # Onboarding
    path('onboarding/',      views.onboarding,       name='onboarding'),
    path('onboarding/save/', views.save_onboarding,  name='save_onboarding'),

    # Tribe actions
    path('join/<int:tribe_id>/',  views.join_tribe,  name='join_tribe'),
    path('leave/<int:tribe_id>/', views.leave_tribe, name='leave_tribe'),
]
