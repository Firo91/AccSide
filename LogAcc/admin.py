from django.contrib import admin
from .models import Budget, Expense, CustomUser, Team, UserRole
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms
from .forms import CustomUserAdminForm
# Register your models here.

admin.site.register(Budget)
admin.site.register(Expense)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm  # Assumes you've added the form as provided earlier
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name', 'team', 'role')}),  # Added 'role'
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'password1', 'password2', 'team', 'role'),  # Added 'role'
        }),
    )
    list_display = ('username', 'name', 'team', 'role', 'is_staff')  # Added 'role'
    list_filter = ['role', 'team']  # Added filtering by role and team
    search_fields = ('username', 'name', 'team__name')
    ordering = ('username',)

    actions = ['set_as_team_leader', 'set_as_regular_user']  # Added actions

    def set_as_team_leader(self, request, queryset):
        queryset.update(role=UserRole.TEAM_LEADER)
    set_as_team_leader.short_description = "Set selected users as Team Leaders"

    def set_as_regular_user(self, request, queryset):
        queryset.update(role=UserRole.REGULAR_USER)
    set_as_regular_user.short_description = "Set selected users as Regular Users"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name']
    
admin.site.site_header = "Your Admin Panel"
admin.site.site_title = "Your Admin Site"
admin.site.index_title = "Welcome to Your Admin Panel"