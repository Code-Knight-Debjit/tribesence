from django.db import models
from django.contrib.auth.models import User


class Tribe(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food & Drink'),
        ('art', 'Art & Culture'),
        ('outdoors', 'Outdoors'),
        ('music', 'Live Music'),
        ('wellness', 'Wellness'),
        ('books', 'Books & Talks'),
        ('comedy', 'Comedy & Shows'),
        ('tech', 'Tech & Ideas'),
        ('travel', 'Travel & Trips'),
        ('social', 'Social'),
    ]

    name = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='🔥')
    icon_bg = models.CharField(max_length=20, default='#FDBA9A')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='social')
    tags = models.CharField(max_length=200, help_text='Comma-separated tags')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tribes')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def member_count(self):
        return self.memberships.filter(is_active=True).count()


class Membership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Admin'),
        ('creator', 'Creator'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    tribe = models.ForeignKey(Tribe, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'tribe')

    def __str__(self):
        return f'{self.user.username} → {self.tribe.name}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    onboarding_complete = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    avatar_color = models.CharField(max_length=20, default='#E76F51')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Profile({self.user.username})'


class OnboardingPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    tribe_name = models.CharField(max_length=120, blank=True)
    is_planning_event = models.BooleanField(null=True, blank=True)
    event_preferences = models.JSONField(default=list)
    tribe_vibe = models.JSONField(default=list)
    age_group = models.CharField(max_length=20, blank=True)
    travel_preference = models.CharField(max_length=50, blank=True)
    priorities = models.JSONField(default=list)
    availability_days = models.IntegerField(default=2)
    event_frequency = models.IntegerField(default=2)
    group_size = models.IntegerField(default=10)
    completed_step = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Prefs({self.user.username})'
