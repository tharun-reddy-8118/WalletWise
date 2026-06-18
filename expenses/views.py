from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Category, Income, Source, UserPreference
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
import csv
import json

def get_currency(user):
    pref, _ = UserPreference.objects.get_or_create(user=user)
    return pref.currency

@login_required(login_url='/authentication/login')
def dashboard(request):
    expenses = Expense.objects.filter(owner=request.user)
    incomes = Income.objects.filter(owner=request.user)
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0.00
    balance = float(total_income) - float(total_expense)
    currency = get_currency(request.user)
    
    expense_trend = list(expenses.values('date').annotate(total=Sum('amount')).order_by('date'))
    income_trend = list(incomes.values('date').annotate(total=Sum('amount')).order_by('date'))
    
    expense_data = [{'date': str(e['date']), 'total': float(e['total'])} for e in expense_trend]
    income_data = [{'date': str(i['date']), 'total': float(i['total'])} for i in income_trend]
    
    context = {
        'total_expense': total_expense,
        'total_income': total_income,
        'balance': balance,
        'currency': currency,
        'recent_expenses': expenses.order_by('-date')[:5],
        'recent_incomes': incomes.order_by('-date')[:5],
        'expense_data': json.dumps(expense_data),
        'income_data': json.dumps(income_data)
    }
    return render(request, 'expenses/dashboard.html', context)

@login_required(login_url='/authentication/login')
def expense_list(request):
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')
    context = {'expenses': expenses, 'currency': get_currency(request.user)}
    return render(request, 'expenses/index.html', context)

@login_required(login_url='/authentication/login')
def add_expense(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category = request.POST.get('category')

        if not amount or not description or not date:
            messages.error(request, 'All fields are required.')
            return render(request, 'expenses/add_expense.html')

        Expense.objects.create(owner=request.user, amount=amount, date=date, description=description, category=category)
        messages.success(request, 'Expense saved successfully.')
        return redirect('expenses')
    return render(request, 'expenses/add_expense.html')

@login_required(login_url='/authentication/login')
def income_list(request):
    incomes = Income.objects.filter(owner=request.user).order_by('-date')
    context = {'incomes': incomes, 'currency': get_currency(request.user)}
    return render(request, 'income/index.html', context)

@login_required(login_url='/authentication/login')
def add_income(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('income_date')
        source = request.POST.get('source')

        if not amount or not description or not date:
            messages.error(request, 'All fields are required.')
            return render(request, 'income/add_income.html')

        Income.objects.create(owner=request.user, amount=amount, date=date, description=description, source=source)
        messages.success(request, 'Income saved successfully.')
        return redirect('income')
    return render(request, 'income/add_income.html')

@login_required(login_url='/authentication/login')
def expense_summary(request):
    expenses = Expense.objects.filter(owner=request.user)
    summary = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    context = {'summary': summary, 'currency': get_currency(request.user)}
    return render(request, 'summary/expenses.html', context)

@login_required(login_url='/authentication/login')
def income_summary(request):
    incomes = Income.objects.filter(owner=request.user)
    summary = incomes.values('source').annotate(total=Sum('amount')).order_by('-total')
    context = {'summary': summary, 'currency': get_currency(request.user)}
    return render(request, 'summary/income.html', context)

@login_required(login_url='/authentication/login')
def export_expenses_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Description', 'Category', 'Amount'])
    for expense in Expense.objects.filter(owner=request.user).order_by('-date'):
        writer.writerow([expense.date, expense.description, expense.category, expense.amount])
    return response

@login_required(login_url='/authentication/login')
def export_income_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="income.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Description', 'Source', 'Amount'])
    for income in Income.objects.filter(owner=request.user).order_by('-date'):
        writer.writerow([income.date, income.description, income.source, income.amount])
    return response

@login_required(login_url='/authentication/login')
def settings_view(request):
    pref, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        currency = request.POST.get('currency')
        pref.currency = currency
        pref.save()
        messages.success(request, 'Settings saved successfully.')
        return redirect('settings')
    return render(request, 'preferences/index.html', {'currency': pref.currency})
