import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server-side rendering

import matplotlib.pyplot as plt
import io, base64
import yfinance as yf

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from transactions.models import Transaction
from investments.models import Investment
from shared_budgeting.models import SharedBudget, Expense
from reportlab.pdfgen import canvas


# ----------------------------------------
# 🔧 Shared: Convert Plot to Base64
# ----------------------------------------
def plot_to_base64():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()


# ----------------------------------------
# 🔍 Shared: Filter Transactions by User/Date
# ----------------------------------------
def get_filtered_transactions(user, date_from=None, date_to=None):
    txns = Transaction.objects.filter(user=user)
    if date_from:
        txns = txns.filter(date__gte=date_from)
    if date_to:
        txns = txns.filter(date__lte=date_to)
    return txns


# ----------------------------------------
# 📊 Main Financial Report View
# ----------------------------------------
@login_required
def financial_report(request):
    context = {}
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    transactions = get_filtered_transactions(request.user, date_from, date_to)

    # === Totals
    income = transactions.filter(category='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = transactions.filter(category='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_savings = income - expense

    context.update({
        'total_income': income,
        'total_expense': expense,
        'net_savings': net_savings
    })

    # === Pie Chart: Income vs Expenses
    if income or expense:
        plt.figure(figsize=(5, 5))
        plt.pie([income, expense], labels=['Income', 'Expenses'], colors=['green', 'red'],
                autopct='%1.1f%%', startangle=90)
        plt.title("Income vs Expenses")
        context['pie_chart'] = plot_to_base64()

    # === Bar Chart: Monthly Trends
    monthly_data = (
        transactions.annotate(month=TruncMonth('date'))
        .values('month', 'category')
        .annotate(total=Sum('amount'))
    )
    income_data = {d['month']: d['total'] for d in monthly_data if d['category'] == 'income'}
    expense_data = {d['month']: d['total'] for d in monthly_data if d['category'] == 'expense'}
    months = sorted(set(income_data) | set(expense_data))

    if months:
        income_vals = [income_data.get(m, 0) for m in months]
        expense_vals = [expense_data.get(m, 0) for m in months]

        plt.figure(figsize=(8, 4))
        plt.bar(months, income_vals, label='Income', color='green')
        plt.bar(months, expense_vals, label='Expenses', color='red', alpha=0.7)
        plt.xticks(rotation=45)
        plt.xlabel("Month")
        plt.ylabel("Amount ($)")
        plt.title("Monthly Income vs Expenses")
        plt.legend()
        context['bar_chart'] = plot_to_base64()

    # === Investment Chart
    investments = Investment.objects.filter(user=request.user)
    labels, values = [], []
    for inv in investments:
        try:
            price = yf.Ticker(inv.symbol).info.get('regularMarketPrice') or 0
            labels.append(inv.symbol)
            values.append(round(price * inv.quantity, 2))
        except Exception:
            continue

    if labels:
        plt.figure(figsize=(6, 4))
        plt.bar(labels, values, color='steelblue')
        plt.title("📈 Investment Portfolio Value")
        plt.ylabel("Total Value ($)")
        context['investment_chart'] = plot_to_base64()

    # === Shared Budget Chart
    budgets = SharedBudget.objects.filter(members=request.user)
    shared_totals = Expense.objects.filter(budget__in=budgets).values('budget__name').annotate(total=Sum('amount'))

    if shared_totals:
        sb_labels = [b['budget__name'] for b in shared_totals]
        sb_values = [float(b['total']) for b in shared_totals]

        plt.figure(figsize=(6, 4))
        plt.pie(sb_values, labels=sb_labels, autopct='%1.1f%%', startangle=90)
        plt.title("🤝 Shared Budget Breakdown")
        context['shared_budget_chart'] = plot_to_base64()

    return render(request, 'reports/financial_report.html', context)


# ----------------------------------------
# 📄 PDF Export View
# ----------------------------------------
@login_required
def generate_pdf(request):
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    transactions = get_filtered_transactions(request.user, date_from, date_to)

    income = transactions.filter(category='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = transactions.filter(category='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    savings = income - expense

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="financial_report.pdf"'
    pdf = canvas.Canvas(response)

    # PDF Content
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, "📊 Financial Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 750, f"Total Income: ${income:.2f}")
    pdf.drawString(100, 730, f"Total Expenses: ${expense:.2f}")
    pdf.drawString(100, 710, f"Net Savings: ${savings:.2f}")
    pdf.drawString(100, 690, f"Date Range: {date_from or 'All'} to {date_to or 'All'}")

    pdf.save()
    return response
