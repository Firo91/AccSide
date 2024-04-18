from django.contrib import admin
from .models import Budget, Expense, Team, CustomUser
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

admin.site.register(Budget)
admin.site.register(Expense)
admin.site.register(Team)

class CustomDefaultUserAdmin(DefaultUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields', {'fields': ('passphrase', 'current_team')}),
    )

@admin.register(CustomUser)
class CustomUserAdmin(CustomDefaultUserAdmin):
    # Add 'teams' to list_display to display it in the users list
    list_display = CustomDefaultUserAdmin.list_display + ('teams_list',)

    def teams_list(self, obj):
        return ", ".join([team.name for team in obj.teams.all()])

    teams_list.short_description = 'Teams'