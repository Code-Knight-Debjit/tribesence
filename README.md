# Tribesence — Django Setup Guide

## Quick Start

```bash
# 1. Create & activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Create a superuser (optional, for /admin)
python manage.py createsuperuser

# 5. Start the dev server
python manage.py runserver
```

Then open http://127.0.0.1:8000

## URL Map

| URL                    | Page                     |
|------------------------|--------------------------|
| /                      | Landing page (hero + features) |
| /tribes/explore/       | Explore feed with tribe cards |
| /tribes/onboarding/    | 7-step onboarding flow   |
| /accounts/login/       | Sign in                  |
| /accounts/signup/      | Create account           |
| /accounts/logout/      | Log out                  |
| /admin/                | Django admin             |

## Project Structure

```
tribesence/
├── manage.py
├── requirements.txt
├── tribesence/          ← Project config
│   ├── settings.py
│   └── urls.py
├── core/                ← Landing page
│   ├── views.py
│   ├── urls.py
│   └── templates/core/
│       ├── base.html    ← Navbar, global CSS, design tokens
│       └── landing.html ← Hero + waving character animation
├── tribes/              ← Main app
│   ├── models.py        ← Tribe, Membership, Profile, OnboardingPreferences
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/tribes/
│       ├── explore.html
│       └── onboarding.html
└── accounts/            ← Auth
    ├── views.py
    ├── urls.py
    └── templates/accounts/
        ├── login.html
        └── signup.html
```

## Design System

| Token        | Value     | Usage               |
|--------------|-----------|---------------------|
| --primary    | #E76F51   | CTAs only           |
| --secondary  | #264653   | Navbar only         |
| --accent     | #E9C46A   | Tags only           |
| --bg         | #F4EDE4   | Page background     |
| --surface    | #FAF9F6   | Cards               |

## Notes

- Google Sign-In button is UI-only (shows alert). Wire up `python-social-auth` or `allauth` to activate.
- Onboarding step data is saved in-memory in JS; Django backend models are ready for full persistence.
- The hero animation: left character waves hand with CSS `@keyframes waveHand`, group of 3 on the right has clean arms with no floating extras.
