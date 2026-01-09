# finances/views.py
from decimal import Decimal  # 🔑 Importação essencial!
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction
from .forms import TransactionForm
import plotly.express as px
from plotly.offline import plot

@login_required
def dashboard(request):
    user = request.user
    expenses = Transaction.objects.filter(user=user, type='expense')
    incomes = Transaction.objects.filter(user=user, type='income')

    # Soma total de receitas e despesas (como Decimal)
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    balance = total_income - total_expense  # ✅ Agora ambos são Decimal!

    # Preparar dados para o gráfico (converter para float só aqui)
    expense_data = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    categories = []
    totals_float = []
    for item in expense_data:
        if item['total'] is not None:
            categories.append(item['category'])
            totals_float.append(float(item['total']))

    chart = ""
    if categories:
        try:
            # Paleta de cores suaves que combinam com seu tema escuro
            colors = [
                '#818cf8', '#6366f1', '#a5b4fc',
                '#6ee7b7', '#34d399', '#10b981',
                '#fca5a5', '#f87171', '#ef4444',
                '#fcd34d', '#fbbf24'
            ][:len(categories)]  # Limita ao número de categorias

            fig = px.pie(
                names=categories,
                values=totals_float,
                title="",
                color_discrete_sequence=colors,
                hole=0.4  # Torna o gráfico um "donut" (mais moderno)
            )

            # 🔑 Ajustes ESSENCIAIS para tema escuro
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',      # Fundo externo transparente
                plot_bgcolor='rgba(0,0,0,0)',       # Fundo do gráfico transparente
                font=dict(color='#cbd5e1', size=14), # Texto claro e legível
                title=dict(
                    text="",
                    font=dict(size=18, color='#f1f5f9'),
                    x=0.5,
                    xanchor='center'
                ),
                margin=dict(t=50, b=20, l=20, r=20),
                showlegend=True,
                legend=dict(
                    font=dict(color='#cbd5e1'),
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                )
            )

            # Melhora os rótulos dentro das fatias
            fig.update_traces(
                textposition='inside',
                textinfo='percent',
                insidetextfont=dict(color='#0f172a', size=12, weight='bold'),
                hovertemplate='<b>%{label}</b><br>R$ %{value:.2f}<extra></extra>'
            )

            chart = plot(fig, output_type='div', include_plotlyjs=False)
        except Exception as e:
            print("Erro no gráfico:", e)
            chart = "<p style='color: #fca5a5; text-align: center;'>Erro ao carregar gráfico.</p>"

    # Transações recentes
    recent_transactions = []
    for trans in Transaction.objects.filter(user=user).order_by('-date', '-created_at')[:10]:
        recent_transactions.append({
            'id': trans.id,
            'type': trans.type,
            'amount': trans.amount,
            'category': trans.category,
            'description': trans.description,
            'date': trans.date,
            'is_income': trans.type == 'income',
            'color': '#10b981' if trans.type == 'income' else '#ef4444',
        })

    return render(request, 'finances/dashboard.html', {
        'chart': chart,
        'balance': balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'recent_transactions': recent_transactions,
    })

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'finances/transaction_form.html', {'form': form})

@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    transaction.delete()
    return redirect('dashboard')