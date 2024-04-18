from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, is_password_usable

class CustomUser(AbstractUser):
    current_team = models.ForeignKey('LogAcc.Team', on_delete=models.SET_NULL, null=True, blank=True)
    passphrase = models.CharField(max_length=200, null=True, blank=True)

class Team(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField('LogAcc.CustomUser', related_name='teams')

class Budget(models.Model):
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=0)
    date_set = models.DateField(default=timezone.now)
    locked = models.BooleanField(default=False)
    user = models.ManyToManyField(CustomUser)
    team = models.OneToOneField(Team, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk and Budget.objects.filter(team=self.team).exists():
            raise ValidationError('There can be only one Budget instance per team')
        return super(Budget, self).save(*args, **kwargs)

    class Meta:
        permissions = [
            ("can_toggle_lock", "Can toggle lock status"),
        ]

class Expense(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, help_text="Brief description of the expense")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes or details about the expense")
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    date = models.DateField(auto_now_add=True)

    class Meta:
        # If you already have a Meta class, simply add to the permissions list.
        permissions = [
            ("export_all_users", "Can export expenses for all users"),
        ]
        
class ButtonPressLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=255)
    
class BudgetHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team =  models.ForeignKey(Team, on_delete=models.CASCADE)
    old_value = models.DecimalField(max_digits=10, decimal_places=2)
    date_set = models.DateField()