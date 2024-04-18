from django.http import HttpResponse
from django.template import loader
from django.views import View
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from .models import Expense, Budget, ButtonPressLog, BudgetHistory
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
from .models import Expense, Team, CustomUser
from .forms import ExpenseForm, RegisterForm, BudgetForm, PasswordResetForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import datetime
from datetime import date, timedelta
from django.db.models import Sum
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

class HomePageView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            team = self.request.user.current_team  # Get the user's team
            context['current_team'] = team

            # Calculate total expenses for the team
            total_expenses = Expense.objects.filter(team=team).aggregate(Sum('amount'))['amount__sum'] or 0
            context['amount_spent'] = total_expenses

            # Get the team's budget
            try:
                context['budget'] = Budget.objects.filter(team=team).latest('date_set')
                context['remaining'] = context['budget'].monthly_limit - total_expenses
            except Budget.DoesNotExist:
                context['budget'] = None
                context['remaining'] = None

            # Fetching expenses of the authenticated user for the team
            context['user_expenses'] = Expense.objects.filter(user=self.request.user, team=team)

        else:
            context['budget'] = None
            context['user_expenses'] = []

        return context
    
def change_team(request):
    if request.method == 'POST':
        team_id = request.POST.get('team')
        team = Team.objects.get(id=team_id)
        request.user.current_team = team
        request.user.save()
    return redirect('home')
    
def export_to_excel(request, username=None):
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    day = request.GET.get('day', None)

    # If no values are provided, default to today's values
    today = datetime.date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month
    day = int(day) if day else today.day

    if username:
        target_user = CustomUser.objects.get(username=username)
        expenses = Expense.objects.filter(user=target_user)
    else:
        # Check if the user has permission to export all data
        if request.user.has_perm('your_app_name.export_all_users'):
            expenses = Expense.objects.all()
        else:
            expenses = Expense.objects.filter(user=request.user)

    expenses = expenses.filter(date__year=year)

    # Filter month and day only if they are provided
    if month:
        expenses = expenses.filter(date__month=month)
    if day:
        expenses = expenses.filter(date__day=day)

    # Convert the queryset to a dataframe
    df = pd.DataFrame.from_records(expenses.values('title', 'notes', 'amount', 'date', 'team__name'))

    # Rename the team column
    df.rename(columns={'team__name': 'team'}, inplace=True)

    # Fetch the singular Budget object for the entire system
    budget = Budget.objects.first()

    # If the Budget exists
    if budget:
        monthly_limit = budget.monthly_limit
    else:
        # Handle case when no budget object is available
        monthly_limit = 0  # or whatever default or error handling you prefer

    # Calculate the remaining budget using the monthly_limit
    df['remaining_budget'] = df['amount'].cumsum().apply(lambda x: monthly_limit - x)


    # Convert the dataframe to an excel sheet
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=expenses.xlsx'

    wb = openpyxl.Workbook()
    ws = wb.active

    for row in dataframe_to_rows(df, index=False, header=True):
        ws.append(row)

    wb.save(response)

    return response 
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('home')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'add_expense.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            new_team_name = form.cleaned_data.get('new_team')
            if new_team_name:
                # Create a new team and add the user to it
                team = Team.objects.create(name=new_team_name)
                team.users.add(user)
            else:
                # Add the user to the selected team
                team = form.cleaned_data.get('team')
                if team:
                    team.users.add(user)
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to home page after successful login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def set_budget(request):
    current_month = date.today().month
    current_year = date.today().year
    team = request.user.current_team
    budget_instance = None

    try:
        # Check if a budget has been set for the current month, year, and team
        budget_instance = Budget.objects.get(date_set__month=current_month, date_set__year=current_year, team=team)

        # Check if budget is locked
        if budget_instance.locked and not request.user.is_staff:
            message = "Budget for this month is already set and locked."
            return render(request, 'locked_budget.html', {'message': message})
    except Budget.DoesNotExist:
        try:
            # Fetch the budget from the previous month to pre-fill the form
            last_month = current_month - 1 or 12
            last_month_year = current_year if current_month != 1 else current_year - 1
            budget_instance = Budget.objects.get(date_set__month=last_month, date_set__year=last_month_year, team=team)
        except Budget.DoesNotExist:
            pass

    if request.method == "POST":
        if 'toggle_lock' in request.POST:
            # Logic to toggle the lock status
            budget_instance.locked = not budget_instance.locked
            budget_instance.save()
            
            # Log the button press action to the ButtonPressLog
            ButtonPressLog.objects.create(user=request.user, action="Toggle Lock")

            return redirect('set_budget')  # Redirect back to the same page
        else:
            # Save the current budget value to the history before updating it, if it exists
            if budget_instance:
                BudgetHistory.objects.create(user=request.user, old_value=budget_instance.monthly_limit, date_set=budget_instance.date_set)

            form = BudgetForm(request.POST, instance=budget_instance, user=request.user)
            if form.is_valid():
                budget = form.save(commit=False)
                budget.date_set = date.today()
                budget.team = form.cleaned_data.get('team')  # Save the team
                budget.save()
                return redirect('home')
    else:
            form = BudgetForm(instance=budget_instance, user=request.user)

    return render(request, 'set_budget.html', {'form': form, 'budget': budget_instance})

def budget_history(request):
    history = BudgetHistory.objects.filter(user=request.user).order_by('-date_set')
    return render(request, 'budget_history.html', {'history': history})

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            passphrase = form.cleaned_data["passphrase"]
            new_password = form.cleaned_data["new_password"]
            try:
                user = CustomUser.objects.get(username=username)
                if user.passphrase == passphrase:  # compare input passphrase with stored passphrase
                    user.set_password(new_password)
                    user.save()
                    # Update session hash to keep the user logged in after password change
                    update_session_auth_hash(request, user)
                    return redirect('home')
                else:
                    messages.error(request, 'Incorrect passphrase.')
            except ObjectDoesNotExist:
                messages.error(request, 'User does not exist.')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})