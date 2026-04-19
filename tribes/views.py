import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Tribe, Membership, OnboardingPreferences, Profile
from django.contrib.auth.models import User

SAMPLE_TRIBES = [
    {'id': 1,  'icon': '🍜', 'icon_bg': '#FDBA9A', 'name': 'Sunday Ramen Crew',      'description': "We hunt the city's best bowls every Sunday morning. Rain or shine, slurp on.",      'tags': 'Food,Culture',   'members': 34},
    {'id': 2,  'icon': '🎨', 'icon_bg': '#C8E6C9', 'name': 'Canvas & Conversation',  'description': 'Monthly gallery visits with dinner after. Art + honest opinions + wine.',            'tags': 'Art,Social',     'members': 21},
    {'id': 3,  'icon': '🏕️', 'icon_bg': '#B0BEC5', 'name': 'Weekend Wanderers',      'description': 'Day hikes, camping, and sunsets. No experience needed — just show up.',             'tags': 'Outdoors,Travel','members': 58},
    {'id': 4,  'icon': '🎭', 'icon_bg': '#F8BBD0', 'name': 'Improv & Easy Laughs',   'description': 'Thursday night improv workshops. Zero pressure, maximum laughter.',                  'tags': 'Comedy,Social',  'members': 17},
    {'id': 5,  'icon': '📚', 'icon_bg': '#E1BEE7', 'name': 'Slow Readers Society',   'description': 'We read one book a month and talk about it over a long dinner.',                     'tags': 'Books,Dinner',   'members': 29},
    {'id': 6,  'icon': '🌮', 'icon_bg': '#FFE0B2', 'name': 'Taco Tuesday Tribe',     'description': 'Every Tuesday, a new taco spot. We vote on the next place together.',                'tags': 'Food,Weekly',    'members': 42},
    {'id': 7,  'icon': '🚴', 'icon_bg': '#B2EBF2', 'name': 'Dawn Cyclists',          'description': '6am rides through the city before it wakes up. Coffee after, always.',               'tags': 'Fitness,Outdoors','members': 19},
    {'id': 8,  'icon': '🎵', 'icon_bg': '#D7CCC8', 'name': 'Live Music Locals',      'description': 'We go to a local gig together every other week. All genres welcome.',                'tags': 'Music,Nights',   'members': 37},
    {'id': 9,  'icon': '🍷', 'icon_bg': '#FFCCBC', 'name': 'Natural Wine Club',      'description': 'Exploring biodynamic and natural wines without the pretension.',                     'tags': 'Wine,Social',    'members': 24},
    {'id': 10, 'icon': '🤿', 'icon_bg': '#B2DFDB', 'name': 'Open Water Collective',  'description': 'Sea swimming, lake dips, and open water adventures year-round.',                     'tags': 'Outdoors,Sport', 'members': 15},
]


def explore(request):
    """Explore Tribes page — with Explore button + tribe detail modal."""
    db_tribes = list(Tribe.objects.filter(is_active=True).values(
        'id', 'name', 'description', 'icon', 'icon_bg', 'tags'
    ))
    for t in db_tribes:
        t['members'] = Tribe.objects.get(id=t['id']).member_count()

    all_tribes = SAMPLE_TRIBES + db_tribes
    return render(request, 'tribes/explore.html', {'tribes': all_tribes})


def explore_events(request):
    """Explore Events page — Eventbrite-inspired layout.
    Event data is rendered client-side from JS constants in the template.
    Future: pass real Event model querysets here.
    """
    return render(request, 'tribes/explore_events.html', {
        'events': [],   # placeholder — JS handles the data in this phase
    })


@login_required
def onboarding(request):
    prefs, _ = OnboardingPreferences.objects.get_or_create(user=request.user)
    step = int(request.GET.get('step', 1))
    return render(request, 'tribes/onboarding.html', {'step': step, 'prefs': prefs})


@login_required
@require_POST
def save_onboarding(request):
    prefs, _ = OnboardingPreferences.objects.get_or_create(user=request.user)
    step = int(request.POST.get('step', 1))

    if step == 1:
        prefs.tribe_name = request.POST.get('tribe_name', '')
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.phone    = request.POST.get('phone', '')
        profile.zip_code = request.POST.get('zip_code', '')
        profile.save()
    elif step == 2:
        prefs.is_planning_event = request.POST.get('planning') == 'yes'
    elif step == 3:
        prefs.event_preferences = request.POST.getlist('events')
    elif step == 4:
        prefs.tribe_vibe = request.POST.getlist('vibe')
    elif step == 5:
        prefs.age_group         = request.POST.get('age_group', '')
        prefs.travel_preference = request.POST.get('travel', '')
    elif step == 6:
        prefs.priorities = request.POST.getlist('priorities')
    elif step == 7:
        prefs.availability_days = int(request.POST.get('avail', 2))
        prefs.event_frequency   = int(request.POST.get('freq', 2))
        prefs.group_size        = int(request.POST.get('size', 10))
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.onboarding_complete = True
        profile.save()

    prefs.completed_step = step
    prefs.save()

    if step >= 7:
        return redirect('explore')
    return redirect(f'/tribes/onboarding/?step={step + 1}')


@login_required
@require_POST
def join_tribe(request, tribe_id):
    tribe = get_object_or_404(Tribe, id=tribe_id)
    membership, created = Membership.objects.get_or_create(
        user=request.user, tribe=tribe,
        defaults={'role': 'member', 'is_active': True}
    )
    if not created:
        membership.is_active = True
        membership.save()
    return JsonResponse({'success': True, 'message': f'Joined {tribe.name}!'})
