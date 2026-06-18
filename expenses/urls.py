from django.contrib import admin
from django.urls import path
from . import views 

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('expenses/', views.expense_list, name="expenses"),
    path('expenses/add/', views.add_expense, name="add-expense"),
    path('income/', views.income_list, name="income"),
    path('income/add/', views.add_income, name="add-income"),
    path('summary/expenses/', views.expense_summary, name="expense-summary"),
    path('summary/income/', views.income_summary, name="income-summary"),
    path('export/expenses/csv/', views.export_expenses_csv, name="export-expenses-csv"),
    path('export/income/csv/', views.export_income_csv, name="export-income-csv"),
    path('settings/', views.settings_view, name="settings"),
]
