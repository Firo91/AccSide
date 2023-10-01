from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Budget(models.Model):
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=0)
    date_set = models.DateField(default=timezone.now)
    locked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk and Budget.objects.exists():
            raise ValidationError('There is can be only one Budget instance')
        return super(Budget, self).save(*args, **kwargs)

    class Meta:
        permissions = [
            ("can_toggle_lock", "Can toggle lock status"),
        ]

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=255)
    
class BudgetHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    old_value = models.DecimalField(max_digits=10, decimal_places=2)
    date_set = models.DateField()