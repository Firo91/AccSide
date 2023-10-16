from django.contrib.auth.models import  AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Team(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, username, name, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staff(self, username, name, password=None, **extra_fields):
        extra_fields.setdefault('role', UserRole.STAFF)
        return self.create_user(username, name, password, **extra_fields)
    
    def create_team_leader(self, username, name, password=None, **extra_fields):
        extra_fields.setdefault('role', UserRole.TEAM_LEADER)
        return self.create_user(username, name, password, **extra_fields)

    def create_superuser(self, username, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        extra_fields.setdefault('role', UserRole.STAFF)
        return self.create_user(username, name, password, **extra_fields)
    
class UserRole(models.TextChoices):
    USER = 'user', 'User'
    STAFF = 'staff', 'Staff'
    TEAM_LEADER = 'leader', 'Team Leader'

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='teams')
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.USER)
    is_approved = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.username

class Budget(models.Model):
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2)  # Allowing decimal places for cents
    date_set = models.DateField(default=timezone.now)
    locked = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # Associating Budget with Team

    def save(self, *args, **kwargs):
        # Allow only one Budget instance per team
        if not self.pk and Budget.objects.filter(team=self.team).exists():
            raise ValidationError('There can be only one Budget instance per team')
        return super(Budget, self).save(*args, **kwargs)

    class Meta:
        permissions = [
            ("can_toggle_lock", "Can toggle lock status"),
        ]

class Expense(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, help_text="Brief description of the expense")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes or details about the expense")
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    date = models.DateField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
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
    old_value = models.DecimalField(max_digits=10, decimal_places=2)
    date_set = models.DateField()