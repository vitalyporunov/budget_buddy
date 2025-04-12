from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Investment
from .forms import InvestmentForm
import yfinance as yf

# -------------------------
# ✅ Fetch Stock Price (Helper Function)
# -------------------------
def fetch_stock_price(symbol):
    """
    Fetch the latest stock or crypto price using Yahoo Finance API via `yfinance`.
    """
    try:
        stock = yf.Ticker(symbol)
        live_price = stock.history(period="1d")['Close'].iloc[-1]  
        return round(live_price, 2)
    except Exception:
        return "N/A"  

# -------------------------
# ✅ List Investments
# -------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Investment
from .forms import InvestmentForm

@login_required
def investment_list(request):
    investments = Investment.objects.filter(user=request.user)

    # Fetch live stock/crypto prices
    investment_data = []
    for investment in investments:
        current_price = fetch_stock_price(investment.symbol)

        try:
            total_value = float(current_price) * investment.quantity
            profit_loss = (float(current_price) - float(investment.purchase_price)) * investment.quantity
        except:
            total_value = profit_loss = 'N/A'

        investment_data.append({
            'investment': investment,
            'current_price': current_price,
            'total_value': total_value,
            'profit_loss': profit_loss,
        })

    return render(request, 'investments/investment_list.html', {'investment_data': investment_data})

# -------------------------
# ✅ Add Investment
# -------------------------
@login_required
def add_investment(request):
    """Handles adding a new investment."""
    form = InvestmentForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        investment = form.save(commit=False)
        investment.user = request.user
        investment.save()
        return redirect('investment_list')

    return render(request, 'investments/add_investment.html', {'form': form})

# -------------------------
# ✅ Delete Investment
# -------------------------
@login_required
def delete_investment(request, investment_id):
    """Handles deleting an investment."""
    investment = get_object_or_404(Investment, id=investment_id, user=request.user)

    if request.method == 'POST':
        investment.delete()
        return redirect('investment_list')

    return render(request, 'investments/delete_investment.html', {'investment': investment})
