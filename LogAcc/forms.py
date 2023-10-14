from django import forms
from .models import Expense, User, Budget, Team
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'notes', 'amount']  # Assuming these fields exist in your Expense model

class TeamUserCreationForm(UserCreationForm):
    team_name = forms.CharField(required=True)
    create_new_team = forms.BooleanField(
        required=False,
        initial=False,
        help_text='Check this box to create a new team'
    )

    class Meta:
        model = User
        fields = ("username", "team_name", "create_new_team", "password1", "password2")

    def clean(self):
        cleaned_data = super().clean()
        team_name = cleaned_data.get('team_name')
        create_new_team = cleaned_data.get('create_new_team')

        if not create_new_team:
            # If not creating a new team, check if the provided team name exists
            if not Team.objects.filter(name=team_name).exists():
                self.add_error(
                    'team_name',
                    forms.ValidationError("This team does not exist. Uncheck 'create new team' to create it.")
                )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        team_name = self.cleaned_data.get('team_name')
        create_new_team = self.cleaned_data.get('create_new_team')

        if commit:
            user.save()
            
            if create_new_team:
                # Create a new team and associate with the user
                Team.objects.create(name=team_name)
            else:
                # Associate the user with the existing team
                team = Team.objects.get(name=team_name)
            
            # Additional code for assigning the user to the team, if needed

        return user

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['monthly_limit']
