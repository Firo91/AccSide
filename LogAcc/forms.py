from django import forms
from .models import Expense, Budget, Team, CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class ExpenseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ExpenseForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['team'] = forms.ModelChoiceField(queryset=user.teams.all())

    class Meta:
        model = Expense
        fields = ['title', 'notes', 'amount', 'team'] 

class RegisterForm(UserCreationForm):
    team = forms.ModelChoiceField(queryset=Team.objects.all(), required=False)
    new_team = forms.CharField(max_length=255, required=False)
    passphrase = forms.CharField(max_length=200, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'team', 'new_team', 'passphrase']

class BudgetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(BudgetForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['team'] = forms.ModelChoiceField(queryset=user.teams.all())

    class Meta:
        model = Budget
        fields = ['monthly_limit', 'team']  # Include 'team' in the fields
        
class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150)
    passphrase = forms.CharField(max_length=200)
    new_password = forms.CharField(widget=forms.PasswordInput)
