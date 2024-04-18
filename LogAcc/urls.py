from django.urls import path
from .views import HomePageView, budget_history, export_to_excel, set_budget, add_expense, login_view, register_view, logout_view, change_team, password_reset_request

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('add-expense/', add_expense, name='add_expense'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('export/', export_to_excel, name='export_to_excel'),
    path('set_budget/', set_budget, name='set_budget'),
    path('export_to_excel/<str:username>/', export_to_excel, name='export_to_excel_user'),
    path('budget_history/', budget_history, name='budget_history'),
    path('change_team/', change_team, name='change_team'),
    path('reset_password/', password_reset_request, name='reset_password'),
]