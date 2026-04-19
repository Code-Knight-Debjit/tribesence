import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Tribe, Membership, OnboardingPreferences, Profile
from django.contrib.auth.models import User

# ─────────────────────────────────────────────
# SAMPLE DATA (used for explore pages)
# ─────────────────────────────────────────────
SAMPLE_TRIBES = [
    {'id': 1,  'icon': '🍜', 'icon_bg': '#FDBA9A', 'name': 'Sunday Ramen Crew',     'description': "We hunt the city's best bowls every Sunday morning. Rain or shine, slurp on.",     'tags': 'Food,Culture',    'members': 34},
    {'id': 2,  'icon': '🎨', 'icon_bg': '#C8E6C9', 'name': 'Canvas & Conversation', 'description': 'Monthly gallery visits with dinner after. Art + honest opinions + wine.',            'tags': 'Art,Social',      'members': 21},
    {'id': 3,  'icon': '🏕️', 'icon_bg': '#B0BEC5', 'name': 'Weekend Wanderers',     'description': 'Day hikes, camping, and sunsets. No experience needed — just show up.',             'tags': 'Outdoors,Travel', 'members': 58},
    {'id': 4,  'icon': '🎭', 'icon_bg': '#F8BBD0', 'name': 'Improv & Easy Laughs',  'description': 'Thursday night improv workshops. Zero pressure, maximum laughter.',                  'tags': 'Comedy,Social',   'members': 17},
    {'id': 5,  'icon': '📚', 'icon_bg': '#E1BEE7', 'name': 'Slow Readers Society',  'description': 'We read one book a month and talk about it over a long dinner.',                     'tags': 'Books,Dinner',    'members': 29},
    {'id': 6,  'icon': '🌮', 'icon_bg': '#FFE0B2', 'name': 'Taco Tuesday Tribe',    'description': 'Every Tuesday, a new taco spot. We vote on the next place together.',                'tags': 'Food,Weekly',     'members': 42},
    {'id': 7,  'icon': '🚴', 'icon_bg': '#B2EBF2', 'name': 'Dawn Cyclists',         'description': '6am rides through the city before it wakes up. Coffee after, always.',               'tags': 'Fitness,Outdoors','members': 19},
    {'id': 8,  'icon': '🎵', 'icon_bg': '#D7CCC8', 'name': 'Live Music Locals',     'description': 'We go to a local gig together every other week. All genres welcome.',                'tags': 'Music,Nights',    'members': 37},
    {'id': 9,  'icon': '🍷', 'icon_bg': '#FFCCBC', 'name': 'Natural Wine Club',     'description': 'Exploring biodynamic and natural wines without the pretension.',                     'tags': 'Wine,Social',     'members': 24},
    {'id': 10, 'icon': '🤿', 'icon_bg': '#B2DFDB', 'name': 'Open Water Collective', 'description': 'Sea swimming, lake dips, and open water adventures year-round.',                     'tags': 'Outdoors,Sport',  'members': 15},
]

# Sample activity lines per tribe id
TRIBE_ACTIVITY = {
    1: ['New ramen spot voted in', 'Sunday meet confirmed', '3 new members joined'],
    2: ['Gallery walk scheduled', 'New photo shared', 'Dinner venue confirmed'],
    3: ['Weekend trail updated', 'Camping kit list posted', '5 RSVPs received'],
    4: ['Thursday session confirmed', 'New sketch uploaded', 'Milestone celebration'],
    5: ['May book decided: Piranesi', 'Dinner venue posted', 'Discussion notes up'],
    6: ['New spot: La Mexicana', 'Tuesday confirmed', 'Menu reviewed'],
    7: ['Route updated', 'New cyclist joined', 'Coffee spot pinned'],
    8: ['Gig confirmed', 'Pre-show meet added', 'Playlist shared'],
    9: ['New bottle reviewed', 'Tasting notes posted', 'Next date set'],
    10:['Swim route updated', 'Safety brief shared', 'New dip spot found'],
}


def _days_since(dt):
    """Return integer days between a datetime and today."""
    if dt is None:
        return 0
    return (date.today() - dt.date()).days


# ─────────────────────────────────────────────
# EXPLORE TRIBES
# ─────────────────────────────────────────────
def explore(request):
    db_tribes = list(Tribe.objects.filter(is_active=True).values(
        'id', 'name', 'description', 'icon', 'icon_bg', 'tags'
    ))
    for t in db_tribes:
        t['members'] = Tribe.objects.get(id=t['id']).member_count()
    all_tribes = SAMPLE_TRIBES + db_tribes
    return render(request, 'tribes/explore.html', {'tribes': all_tribes})


# ─────────────────────────────────────────────
# EXPLORE EVENTS
# ─────────────────────────────────────────────
def explore_events(request):
    """Events fed from JS constants in the template (phase 1).
    Future: pass real Event model queryset here.
    """
    return render(request, 'tribes/explore_events.html', {'events': []})


# ─────────────────────────────────────────────
# MY TRIBES (auth required)
# ─────────────────────────────────────────────
@login_required
def my_tribes(request):
    # Memberships for this user — real DB data only
    memberships = (
        Membership.objects
        .filter(user=request.user, is_active=True)
        .select_related('tribe')
        .order_by('-joined_at')
    )

    joined_items = []
    for ms in memberships:
        tribe = ms.tribe
        activity = TRIBE_ACTIVITY.get(tribe.id, ['Active members online', 'Events planned', 'New content posted'])
        joined_items.append({
            'tribe':      tribe,
            'membership': ms,
            'activity':   activity[:3],
            'events_count': 0,    # extend with Event model later
            'days_since': _days_since(ms.joined_at),
        })

    # Tribes this user created (not via membership — via creator FK)
    created_qs = Tribe.objects.filter(creator=request.user, is_active=True).order_by('-created_at')
    created_items = []
    for tribe in created_qs:
        activity = TRIBE_ACTIVITY.get(tribe.id, ['You created this tribe', 'Members active', 'Share the link'])
        created_items.append({
            'tribe':        tribe,
            'activity':     activity[:3],
            'events_count': 0,
            'days_since':   _days_since(tribe.created_at),
        })

    return render(request, 'tribes/my_tribes.html', {
        'joined_tribes':  joined_items,
        'created_tribes': created_items,
    })


# ─────────────────────────────────────────────
# MY EVENTS (auth required)
# ─────────────────────────────────────────────
@login_required
def my_events(request):
    """
    Until an Event model is built, this view pulls from the user's tribe memberships
    and constructs representative events from those tribes.
    When you add an Event model + Registration model, replace the logic below.
    """
    memberships = (
        Membership.objects
        .filter(user=request.user, is_active=True)
        .select_related('tribe')
    )

    # Build representative upcoming events from the user's tribes
    upcoming_events = []
    past_events = []

    # Hardcoded event seed data keyed by tribe index (replace with real Event queryset)
    EVENT_SEED = [
        {'icon': '🍜', 'bg': '#FDBA9A', 'title': 'Sunday Ramen Crawl — Edition 28',     'day': 18, 'month': 'May', 'time': '10:00 AM', 'location': 'Koramangala, Bangalore', 'price': 'Free',  'category': 'Food',     'status': 'upcoming'},
        {'icon': '🎨', 'bg': '#C8E6C9', 'title': 'Canvas & Conversation — Gallery Walk','day': 23, 'month': 'May', 'time': '7:00 PM',  'location': 'Indiranagar, Bangalore',  'price': '₹200',  'category': 'Art',      'status': 'upcoming'},
        {'icon': '🏕️', 'bg': '#B0BEC5', 'title': 'Weekend Trek: Savandurga Hills',       'day': 25, 'month': 'May', 'time': '5:30 AM',  'location': 'Savandurga, Bangalore',   'price': '₹500',  'category': 'Outdoors', 'status': 'upcoming'},
        {'icon': '🎵', 'bg': '#D7CCC8', 'title': 'Live at The Humming Tree — Jazz',      'day': 19, 'month': 'Apr', 'time': '8:00 PM',  'location': 'Indiranagar, Bangalore',  'price': '₹600',  'category': 'Music',    'status': 'today'},
        {'icon': '📚', 'bg': '#E1BEE7', 'title': 'Slow Readers: April Meetup',           'day': 15, 'month': 'Apr', 'time': '7:00 PM',  'location': 'Church St, Bangalore',    'price': 'Free',  'category': 'Social',   'status': 'past'},
        {'icon': '🌮', 'bg': '#FFE0B2', 'title': 'Taco Tuesday — La Mexicana',           'day':  8, 'month': 'Apr', 'time': '7:00 PM',  'location': 'HSR Layout, Bangalore',   'price': '₹150',  'category': 'Food',     'status': 'past'},
    ]

    joined_tribe_names = {ms.tribe.name for ms in memberships}

    for i, ev in enumerate(EVENT_SEED):
        # Attach a tribe name from the user's memberships (rotate through them)
        tribe_list = list(joined_tribe_names)
        tribe_name = tribe_list[i % len(tribe_list)] if tribe_list else None
        ev_full = dict(ev, id=i + 1, tribe_name=tribe_name)

        if ev['status'] in ('upcoming', 'today'):
            upcoming_events.append(ev_full)
        else:
            past_events.append(ev_full)

    # If user has no memberships, return empty lists
    if not memberships.exists():
        upcoming_events = []
        past_events     = []

    return render(request, 'tribes/my_events.html', {
        'upcoming_events': upcoming_events,
        'past_events':     past_events,
    })


# ─────────────────────────────────────────────
# MY PROFILE (auth required)
# ─────────────────────────────────────────────
@login_required
def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    prefs = getattr(request.user, 'preferences', None)

    tribes_count = Membership.objects.filter(user=request.user, is_active=True).count()
    events_count = 0   # extend with Event/Registration model

    # Compute profile completion percentage
    fields_done = sum([
        bool(request.user.first_name),
        bool(request.user.last_name),
        bool(request.user.email),
        bool(profile.phone),
        bool(profile.bio),
        bool(profile.zip_code),
        bool(prefs and prefs.event_preferences),
        bool(prefs and prefs.tribe_vibe),
        bool(prefs and prefs.age_group),
        bool(prefs and prefs.priorities),
    ])
    completion_pct = round((fields_done / 10) * 100)

    return render(request, 'tribes/my_profile.html', {
        'profile':         profile,
        'prefs':           prefs,
        'tribes_count':    tribes_count,
        'events_count':    events_count,
        'completion_pct':  completion_pct,
    })


# ─────────────────────────────────────────────
# ONBOARDING
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# JOIN TRIBE
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# LEAVE TRIBE
# ─────────────────────────────────────────────
@login_required
@require_POST
def leave_tribe(request, tribe_id):
    tribe = get_object_or_404(Tribe, id=tribe_id)
    # Creators cannot leave their own tribe
    if tribe.creator == request.user:
        messages.error(request, "You can't leave a tribe you created. Delete it instead.")
        return redirect('my_tribes')

    Membership.objects.filter(user=request.user, tribe=tribe).update(is_active=False)
    messages.success(request, f'You left {tribe.name}.')
    return redirect('my_tribes')
