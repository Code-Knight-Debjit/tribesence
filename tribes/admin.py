from django.contrib import admin
from .models import Tribe, Membership, Profile, OnboardingPreferences

@admin.register(Tribe)
class TribeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'creator', 'member_count', 'created_at', 'is_active')
    list_filter   = ('category', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'tribe', 'role', 'joined_at', 'is_active')
    list_filter  = ('role', 'is_active')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'onboarding_complete', 'zip_code', 'created_at')

@admin.register(OnboardingPreferences)
class OnboardingPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'tribe_name', 'completed_step', 'updated_at')
