from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from django.views import View, generic
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from .models import Expense, Budget, ButtonPressLog, BudgetHistory
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
from .models import Expense, CustomUser, Team, UserRole
from .forms import ExpenseForm, TeamUserCreationForm, BudgetForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import datetime
from datetime import date, timedelta
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required

class HomePageView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        view_type = self.request.GET.get('view', 'user')  # Default to 'user' if not specified

        if user.is_authenticated:
            try:
                user_team = user.team
                context['budget'] = Budget.objects.filter(team=user_team).latest('date_set')

                total_expenses = Expense.objects.filter(team=user_team).aggregate(Sum('amount'))['amount__sum'] or 0
                context['amount_spent'] = total_expenses
                context['remaining'] = context['budget'].monthly_limit - total_expenses

            except (Budget.DoesNotExist, AttributeError):  
                context['budget'] = None
                context['amount_spent'] = 0
                context['remaining'] = None

            if view_type == "user":
                context['user_expenses'] = Expense.objects.filter(user=user)
            elif view_type == "team":
                context['team_expenses'] = Expense.objects.filter(team=user_team)
            context['view_type'] = view_type

        else:
            context['budget'] = None
            context['user_expenses'] = []
            context['team_expenses'] = []

        return context
 
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
    df = pd.DataFrame.from_records(expenses.values())

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
    
    # Convert the dataframe 
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            # Assume user is part of a team and take the first one
            expense.team = request.user.team
            expense.save()
            return redirect('home')
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})

class register_view(generic.CreateView):
    form_class = TeamUserCreationForm
    success_url = reverse_lazy('login')  # Redirect to your login page after successful registration
    template_name = 'register.html'  # Path to your registration template

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "You've successfully registered!")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "There was an error in your registration.")
        return response

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
    budget_instance = None

    # Assume user is part of a team and take the first one
    user_team = request.user.team

    if not user_team:
        # Handle case where user is not part of any team
        # Maybe redirect them to a page where they can create/join a team
        return redirect('choose_team')

    try:
        # Check if a budget has been set for the current month, year, and team
        budget_instance = Budget.objects.get(date_set__month=current_month, date_set__year=current_year, team=user_team)
        if budget_instance.locked and not request.user.is_staff:
            message = "Budget for this month is already set and locked."
            return render(request, 'locked_budget.html', {'message': message})
    except Budget.DoesNotExist:
        try:
            last_month = current_month - 1 or 12
            last_month_year = current_year if current_month != 1 else current_year - 1
            budget_instance = Budget.objects.get(date_set__month=last_month, date_set__year=last_month_year, team=user_team)
        except Budget.DoesNotExist:
            pass

    if request.method == "POST":
        if 'toggle_lock' in request.POST and budget_instance:
            budget_instance.locked = not budget_instance.locked
            budget_instance.save()
            ButtonPressLog.objects.create(user=request.user, action="Toggle Lock")
            return redirect('set_budget')  
        else:
            if budget_instance:
                BudgetHistory.objects.create(user=request.user, old_value=budget_instance.monthly_limit, date_set=budget_instance.date_set)

            form = BudgetForm(request.POST, instance=budget_instance)
            if form.is_valid():
                budget = form.save(commit=False)
                budget.date_set = date.today()
                budget.team = user_team  # Assign the team to the budget here
                budget.save()
                return redirect('home')
    else:
        form = BudgetForm(instance=budget_instance)

    return render(request, 'set_budget.html', {'form': form, 'budget': budget_instance})


def budget_history(request):
    history = BudgetHistory.objects.filter(user=request.user).order_by('-date_set')
    return render(request, 'budget_history.html', {'history': history})

def choose_team(request):
    if request.method == "POST":
        team_id = request.POST.get('team_id')
        request.session['team_id'] = team_id
        
        # Update the user's team in the database
        user = request.user
        user.team = Team.objects.get(id=team_id)
        user.save()
        
        return redirect('set_budget')

    teams = Team.objects.all()  # Query all available teams
    return render(request, 'choose_team.html', {'teams': teams})

@login_required
def approve_team_members(request):
    # Check if user is a team leader
    if request.user.role != UserRole.TEAM_LEADER:
        return HttpResponse("Access denied: You are not a team leader.")

    if request.method == "POST":
        member_id = request.POST.get('member_id')
        member = CustomUser.objects.get(id=member_id)
        member.is_approved = True
        member.save()

    # Get all unapproved members in the team leader's team
    members_to_approve = CustomUser.objects.filter(team=request.user.team, is_approved=False)
    return render(request, 'approve_team_members.html', {'members_to_approve': members_to_approve})