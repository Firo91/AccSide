from django import forms
from .models import Expense, User, Budget
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'notes', 'amount']  # Assuming these fields exist in your Expense model

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['monthly_limit']
