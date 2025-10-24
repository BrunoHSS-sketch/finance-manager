from django.db import models
from django.db.models import Sum, Q
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from .models import AccountEntry, Category, Goal
from .forms import AccountEntryForm, CategoryForm, GoalForm
from django.views.generic.base import RedirectView

@login_required
def dashboard(request):
    # --- LÓGICA DE FILTRO DE DATA (BASEADA EM date_added) ---
    now = timezone.now()
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')

    default_date_to = now.date()
    default_date_from = default_date_to - timedelta(days=30)

    try:
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date() if date_from_str else default_date_from
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date() if date_to_str else default_date_to
    except ValueError:
        date_from = default_date_from
        date_to = default_date_to

    base_qs = AccountEntry.objects.filter(
        date_added__date__gte=date_from,
        date_added__date__lte=date_to
    )

    # --- Card 1: Saldo Total (Histórico) ---
    all_receitas = AccountEntry.objects.filter(category__type='R').aggregate(total=Sum('value'))['total'] or Decimal(
        '0.00')
    all_despesas = AccountEntry.objects.filter(category__type='D').aggregate(total=Sum('value'))['total'] or Decimal(
        '0.00')
    saldo_total = all_receitas - all_despesas

    # --- Card 2: Receitas do Período ---
    receitas_periodo = base_qs.filter(category__type='R').aggregate(total=Sum('value'))['total'] or Decimal('0.00')

    # --- Card 3: Despesas do Período ---
    despesas_periodo = base_qs.filter(category__type='D').aggregate(total=Sum('value'))['total'] or Decimal('0.00')

    # --- Gráfico de Barras: Receitas vs Despesas (Últimos 6 meses) ---
    start_month_chart = (now.replace(day=1) - timedelta(days=180)).replace(day=1)
    qs_period_chart = AccountEntry.objects.filter(date_added__gte=start_month_chart)
    monthly = (
        qs_period_chart
        .annotate(month=TruncMonth('date_added'))
        .values('month')
        .annotate(
            total_receitas=Sum('value', filter=models.Q(category__type='R')),
            total_despesas=Sum('value', filter=models.Q(category__type='D'))
        )
        .order_by('month')
    )
    meses = []
    receitas_data = []
    despesas_data = []
    for row in monthly:
        m = row['month']
        meses.append(m.strftime('%b'))
        receitas_data.append(float(row['total_receitas'] or 0))
        despesas_data.append(float(row['total_despesas'] or 0))
    if not meses:
        for i in range(5, -1, -1):
            dt = (now.replace(day=1) - timedelta(days=30 * i))
            meses.append(dt.strftime('%b'))
            receitas_data.append(0)
            despesas_data.append(0)

    # --- CÁLCULO LUCRO MÊS ATUAL vs ANTERIOR ---
    current_year = now.year
    current_month = now.month
    previous_month_date = now - relativedelta(months=1)
    previous_month_year = previous_month_date.year
    previous_month = previous_month_date.month

    current_month_receitas = AccountEntry.objects.filter(
        category__type='R', date_added__year=current_year, date_added__month=current_month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    current_month_despesas = AccountEntry.objects.filter(
        category__type='D', date_added__year=current_year, date_added__month=current_month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    current_month_profit = current_month_receitas - current_month_despesas

    previous_month_receitas = AccountEntry.objects.filter(
        category__type='R', date_added__year=previous_month_year, date_added__month=previous_month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    previous_month_despesas = AccountEntry.objects.filter(
        category__type='D', date_added__year=previous_month_year, date_added__month=previous_month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    previous_month_profit = previous_month_receitas - previous_month_despesas

    has_previous_month_data = AccountEntry.objects.filter(
        date_added__year=previous_month_year, date_added__month=previous_month
    ).exists()

    # --- Gráfico 2: Gastos por Categoria ---
    categorias = []
    for c in Category.objects.filter(type='D'):
        total_gasto = base_qs.filter(category=c).aggregate(total=Sum('value')).get('total') or Decimal('0.00')
        if total_gasto > 0:
            if receitas_periodo > 0:
                percent_of_revenue = round((total_gasto / receitas_periodo) * 100, 2)
            else:
                percent_of_revenue = 0
            categorias.append({
                'name': c.name,
                'total_gasto': float(total_gasto),
                'percent_of_revenue': float(percent_of_revenue),
            })
    categorias.sort(key=lambda item: item['total_gasto'], reverse=True)

    # --- Gráfico 3: REGRA 50/30/20 ---
    gasto_essenciais = \
    base_qs.filter(category__type='D', category__financial_bucket='ESS', category__is_active=True).aggregate(
        total=Sum('value'))['total'] or Decimal('0.00')
    gasto_lazer = \
    base_qs.filter(category__type='D', category__financial_bucket='LAZ', category__is_active=True).aggregate(
        total=Sum('value'))['total'] or Decimal('0.00')
    gasto_investimentos = \
    base_qs.filter(category__type='D', category__financial_bucket='INV', category__is_active=True).aggregate(
        total=Sum('value'))['total'] or Decimal('0.00')

    if receitas_periodo > 0:
        # Metas, Percentagens Receita, Percentagens Meta...
        meta_essenciais, meta_lazer, meta_investimentos = receitas_periodo * Decimal(
            '0.50'), receitas_periodo * Decimal('0.30'), receitas_periodo * Decimal('0.20')
        percent_receita_essenciais = round((gasto_essenciais / receitas_periodo) * 100, 2)
        percent_receita_lazer = round((gasto_lazer / receitas_periodo) * 100, 2)
        percent_receita_investimentos = round((gasto_investimentos / receitas_periodo) * 100, 2)
        perc_utilizado_essenciais = round((gasto_essenciais / meta_essenciais) * 100, 2) if meta_essenciais > 0 else 0
        perc_utilizado_lazer = round((gasto_lazer / meta_lazer) * 100, 2) if meta_lazer > 0 else 0
        perc_utilizado_investimentos = round((gasto_investimentos / meta_investimentos) * 100,
                                             2) if meta_investimentos > 0 else 0
    else:
        # Defaults
        meta_essenciais, meta_lazer, meta_investimentos = Decimal('0.00'), Decimal('0.00'), Decimal('0.00')
        percent_receita_essenciais, percent_receita_lazer, percent_receita_investimentos = Decimal('0.00'), Decimal(
            '0.00'), Decimal('0.00')
        perc_utilizado_essenciais, perc_utilizado_lazer, perc_utilizado_investimentos = 0, 0, 0

    budget_50_30_20 = {
        'essenciais_gasto': float(gasto_essenciais), 'essenciais_meta': float(meta_essenciais),
        'essenciais_percent_receita': float(percent_receita_essenciais),
        'essenciais_perc_utilizado': float(perc_utilizado_essenciais),
        'lazer_gasto': float(gasto_lazer), 'lazer_meta': float(meta_lazer),
        'lazer_percent_receita': float(percent_receita_lazer), 'lazer_perc_utilizado': float(perc_utilizado_lazer),
        'investimentos_gasto': float(gasto_investimentos), 'investimentos_meta': float(meta_investimentos),
        'investimentos_percent_receita': float(percent_receita_investimentos),
        'investimentos_perc_utilizado': float(perc_utilizado_investimentos),
    }

    # --- LÓGICA PARA METAS PRÓXIMAS ---
    upcoming_goals = []
    today = timezone.now().date()
    all_goals_qs = Goal.objects.select_related('linked_category').all()
    all_goals_calculated = []
    for goal in all_goals_qs:
        current_amount_agg = AccountEntry.objects.filter(category=goal.linked_category).aggregate(total=Sum('value'))
        current_amount = current_amount_agg.get('total') or Decimal('0.00')
        is_completed = current_amount >= goal.target_amount
        if not is_completed:
            # Cálculos para metas ativas...
            progress_percent = round((current_amount / goal.target_amount) * 100, 2) if goal.target_amount > 0 else 0
            days_diff = (goal.target_date - today).days
            status = "Em Andamento";
            status_color = "blue"
            if days_diff < 0: status = f"Atrasada em {-days_diff} dia(s)"; status_color = "red"
            all_goals_calculated.append({
                'goal': goal, 'current_amount': float(current_amount), 'progress_percent': float(progress_percent),
                'status': status, 'status_color': status_color,
                'days_remaining': days_diff if days_diff >= 0 else None, 'days_diff_sort': days_diff
            })
    all_goals_calculated.sort(key=lambda x: x['days_diff_sort'])
    upcoming_goals = all_goals_calculated[:3]

    # ===============================================
    # --- BUSCAR TRANSAÇÕES RECENTES ---
    # ===============================================
    recent_transactions = AccountEntry.objects.select_related('category').order_by('-date_added')[
        :5]  # Pega as últimas 5
    # ===============================================

    # Contexto final para o template
    context = {
        'saldo_total': float(saldo_total),
        'receitas_mes': float(receitas_periodo),
        'despesas_mes': float(despesas_periodo),
        'investimentos': float(gasto_investimentos),
        'categorias': categorias,
        'budget': budget_50_30_20,
        'meses': meses,
        'receitas_data': receitas_data,
        'despesas_data': despesas_data,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'current_month_profit': float(current_month_profit),
        'previous_month_profit': float(previous_month_profit),
        'has_previous_month_data': has_previous_month_data,
        'upcoming_goals': upcoming_goals,

        # Adiciona a lista de transações recentes ao contexto
        'recent_transactions': recent_transactions,
    }

    return render(request, 'dashboard.html', context)


# --- O RESTO DAS VIEWS (transactions, categories, goals) ---
# ... (permanecem iguais) ...
@login_required
def transactions_list(request):
    qs = AccountEntry.objects.select_related('category').order_by('-date_added')
    tipo = request.GET.get('type')
    if tipo in ('R', 'D'):
        qs = qs.filter(category__type=tipo)
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    try:
        if date_from_str:
            dt_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            qs = qs.filter(date_added__date__gte=dt_from.date())
        if date_to_str:
            dt_to = datetime.strptime(date_to_str, '%Y-%m-%d')
            qs = qs.filter(date_added__date__lte=dt_to.date())
    except ValueError:
        pass
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = AccountEntryForm()
    context = {
        'entries': page_obj.object_list,
        'form': form,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'transactions.html', context)

@login_required
def transactions_create(request):
    if request.method != 'POST':
        return redirect(reverse('transactions_list'))
    form = AccountEntryForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Transação criada com sucesso.')
        return redirect(reverse('transactions_list'))
    else:
        qs = AccountEntry.objects.select_related('category').order_by('-date_added')
        paginator = Paginator(qs, 12)
        page_obj = paginator.get_page(1)
        context = {
            'entries': page_obj.object_list,
            'form': form,
            'is_paginated': page_obj.has_other_pages(),
            'page_obj': page_obj,
        }
        messages.error(request, 'Corrija os erros no formulário.')
        return render(request, 'transactions.html', context)

@login_required
def transactions_edit(request, pk):
    obj = get_object_or_404(AccountEntry, pk=pk)
    if request.method == 'POST':
        form = AccountEntryForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transação atualizada.')
            return redirect(reverse('transactions_list'))
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = AccountEntryForm(instance=obj)
    return render(request, 'transactions_edit.html', {'form': form, 'entry': obj})

@login_required
def transactions_delete(request, pk):
    if request.method != 'POST':
        return redirect(reverse('transactions_list'))
    obj = get_object_or_404(AccountEntry, pk=pk)
    obj.delete()
    messages.success(request, 'Transação excluída.')
    return redirect(reverse('transactions_list'))

@login_required
def category_list_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso.')
            return redirect(reverse('category_list_create') + '?status=active')
        else:
            messages.error(request, 'Erro ao criar categoria. Verifique os campos.')
            status_filter = request.GET.get('status', 'active')
    else:
        form = CategoryForm()
        status_filter = request.GET.get('status', 'active')

    if status_filter == 'inactive':
        categories_qs = Category.objects.filter(is_active=False)
    elif status_filter == 'all':
        categories_qs = Category.objects.all()
    else:
        status_filter = 'active'
        categories_qs = Category.objects.filter(is_active=True)

    categories = categories_qs.order_by('type', 'name')

    context = {
        'form': form,
        'categories': categories,
        'current_filter': status_filter
    }
    return render(request, 'categories.html', context)

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    current_filter = request.GET.get('status', 'active')

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso.')
            redirect_url = reverse('category_list_create') + f'?status={current_filter}'
            return redirect(redirect_url)
        else:
            messages.error(request, 'Erro ao atualizar. Verifique os campos.')
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
        'current_filter': current_filter
    }
    return render(request, 'category_edit.html', context)

@login_required
def category_toggle_active(request, pk):
    if request.method != 'POST':
        return redirect('category_list_create')

    category = get_object_or_404(Category, pk=pk)
    category.is_active = not category.is_active
    category.save()

    action = "reativada" if category.is_active else "arquivada"
    messages.success(request, f'Categoria "{category.name}" {action} com sucesso.')

    previous_filter = request.POST.get('current_filter', 'active')
    redirect_url = reverse('category_list_create') + f'?status={previous_filter}'
    return redirect(redirect_url)

@login_required
def category_delete(request, pk):
    if request.method != 'POST':
        return redirect('category_list_create')
    category = get_object_or_404(Category, pk=pk)
    try:
        category.delete()
        messages.success(request, 'Categoria excluída com sucesso.')
    except ValueError as e:
        messages.error(request, f'Erro: {e}')

    redirect_url = reverse('category_list_create') + '?status=active'
    return redirect(redirect_url)

@login_required
def goals_list_create(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meta criada com sucesso.')
            return redirect(reverse('goals_list_create') + '?status=active')
        else:
            messages.error(request, 'Erro ao criar meta. Verifique os campos.')
            status_filter = request.GET.get('status', 'active')
    else:
        form = GoalForm()
        status_filter = request.GET.get('status', 'active')

    goals_qs = Goal.objects.select_related('linked_category').all()
    goals_data = []
    today = timezone.now().date()

    all_goals_calculated = []
    for goal in goals_qs:
        current_amount_agg = AccountEntry.objects.filter(
            category=goal.linked_category
        ).aggregate(total=Sum('value'))
        current_amount = current_amount_agg.get('total') or Decimal('0.00')

        is_completed = current_amount >= goal.target_amount

        progress_percent = 0
        status = "Em Andamento"
        status_color = "blue"
        days_diff = (goal.target_date - today).days

        if is_completed:
            status = "Concluída!"
            status_color = "green"
        elif days_diff < 0:
            status = f"Atrasada em {-days_diff} dia(s)"
            status_color = "red"

        if goal.target_amount > 0:
            progress_percent = round((current_amount / goal.target_amount) * 100, 2)

        all_goals_calculated.append({
            'goal': goal,
            'current_amount': float(current_amount),
            'progress_percent': float(progress_percent),
            'status': status,
            'status_color': status_color,
            'days_remaining': days_diff if days_diff >= 0 and not is_completed else None,
            'is_completed': is_completed,
            'days_diff_sort': days_diff
        })

    if status_filter == 'completed':
        goals_data = [g for g in all_goals_calculated if g['is_completed']]
    elif status_filter == 'all':
        goals_data = all_goals_calculated
        goals_data.sort(key=lambda x: x['days_diff_sort'])
    else:
        status_filter = 'active'
        goals_data = [g for g in all_goals_calculated if not g['is_completed']]
        goals_data.sort(key=lambda x: x['days_diff_sort'])

    context = {
        'form': form,
        'goals_data': goals_data,
        'current_filter': status_filter
    }
    return render(request, 'goals.html', context)

@login_required
def goals_edit(request, pk):
    goal = get_object_or_404(Goal, pk=pk)
    current_filter = request.GET.get('status', 'active')

    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meta atualizada com sucesso.')
            redirect_url = reverse('goals_list_create') + f'?status={current_filter}'
            return redirect(redirect_url)
        else:
            messages.error(request, 'Erro ao atualizar. Verifique os campos.')
    else:
        form = GoalForm(instance=goal)

    context = {
        'form': form,
        'goal': goal,
        'current_filter': current_filter
    }
    return render(request, 'goal_edit.html', context)

@login_required
def goals_delete(request, pk):
    if request.method != 'POST':
        return redirect('goals_list_create')

    goal = get_object_or_404(Goal, pk=pk)
    goal.delete()
    messages.success(request, 'Meta excluída com sucesso.')

    redirect_url = reverse('goals_list_create') + '?status=active'

    return redirect(redirect_url)
