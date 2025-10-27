from django.db import models
from django.db.models import Sum, Q
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required

# Imports de Modelos e Forms (sem alterações)
from .models import (
    AccountEntry, Category, Goal, Account, Transfer,
    InstallmentPlan
)
from .forms import (
    AccountEntryForm, CategoryForm, GoalForm, AccountForm,
    TransferForm, InstallmentEntryForm
)

from django.views.generic.base import RedirectView


# ===============================================
# VIEW: dashboard (Sem alterações)
# ===============================================
@login_required
def dashboard(request):
    # LÓGICA DE FILTRO (Usa 'competence_date')
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

    # --- Query base usa competence_date ---
    base_qs = AccountEntry.objects.filter(
        competence_date__gte=date_from,
        competence_date__lte=date_to
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

    # GRÁFICO (Usa 'competence_date')
    start_month_chart = (now.replace(day=1) - timedelta(days=180)).replace(day=1)
    qs_period_chart = AccountEntry.objects.filter(competence_date__gte=start_month_chart)
    monthly = (
        qs_period_chart
        .annotate(month=TruncMonth('competence_date'))
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

    # CÁLCULO LUCRO (Usa 'competence_date')
    current_year = now.year
    current_month = now.month
    previous_month_date = now - relativedelta(months=1)
    previous_month_year = previous_month_date.year
    previous_month = previous_month_date.month

    current_month_receitas = AccountEntry.objects.filter(
        category__type='R', competence_date__year=current_year, competence_date__month=current_month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    current_month_despesas = AccountEntry.objects.filter(
        category__type='D', competence_date__year=current_year, competence_date__month=current_month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    current_month_profit = current_month_receitas - current_month_despesas

    previous_month_receitas = AccountEntry.objects.filter(
        category__type='R', competence_date__year=previous_month_year, competence_date__month=previous_month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    previous_month_despesas = AccountEntry.objects.filter(
        category__type='D', competence_date__year=previous_month_year, competence_date__month=previous_month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    previous_month_profit = previous_month_receitas - previous_month_despesas

    has_previous_month_data = AccountEntry.objects.filter(
        competence_date__year=previous_month_year, competence_date__month=previous_month
    ).exists()

    # --- Gráfico 2: Gastos por Categoria ---
    categorias = []
    for c in Category.objects.filter(type='D', is_active=True):
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

    # --- TRANSAÇÕES RECENTES ---
    recent_transactions = AccountEntry.objects.select_related('category', 'account').order_by('-competence_date',
                                                                                              '-date_added')[
        :5]

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
        'recent_transactions': recent_transactions,
    }

    return render(request, 'dashboard.html', context)


# --- VIEWS DE TRANSAÇÕES ---

# ===============================================
# VIEW ATUALIZADA: transactions_list
# ===============================================
@login_required
def transactions_list(request):
    """
    Lista Lançamentos (AccountEntry) E Transferências (Transfer)
    numa única lista combinada e paginada.
    """

    # --- 1. Obter filtros ---
    tipo = request.GET.get('type')
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')

    dt_from = None
    dt_to = None
    try:
        if date_from_str:
            dt_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        if date_to_str:
            dt_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
    except ValueError:
        pass  # Mantém dt_from/dt_to como None

    # --- 2. Consultar Lançamentos (AccountEntry) ---
    entries_qs = AccountEntry.objects.select_related(
        'category', 'account', 'installment_plan'
    ).all()

    if tipo in ('R', 'D'):
        entries_qs = entries_qs.filter(category__type=tipo)
    if dt_from:
        entries_qs = entries_qs.filter(competence_date__gte=dt_from)
    if dt_to:
        entries_qs = entries_qs.filter(competence_date__lte=dt_to)

    # --- 3. Consultar Transferências (Transfer) ---
    # O filtro 'tipo' (R/D) não se aplica a transferências
    transfers_qs = Transfer.objects.select_related('account_origin', 'account_destination')

    if dt_from:
        transfers_qs = transfers_qs.filter(date__gte=dt_from)
    if dt_to:
        transfers_qs = transfers_qs.filter(date__lte=dt_to)

    # Só mostramos transferências se o filtro for "Todos" (default)
    if tipo in ('R', 'D'):
        transfers_qs = transfers_qs.none()  # Retorna queryset vazio

    # --- 4. Combinar e Normalizar as duas listas ---
    combined_list = []

    # Adiciona Lançamentos
    for entry in entries_qs:
        combined_list.append({
            'type': 'entry',
            'sort_date': entry.competence_date,  # Usado para ordenar
            'obj': entry
        })

    # Adiciona Transferências
    for transfer in transfers_qs:
        combined_list.append({
            'type': 'transfer',
            'sort_date': transfer.date,  # Usado para ordenar
            'obj': transfer
        })

    # --- 5. Ordenar a lista combinada em Python ---
    combined_list.sort(key=lambda x: (x['sort_date'], x.get('obj_pk', 0)), reverse=True)
    # Note: A ordenação secundária (por PK) não está implementada aqui,
    # mas a ordenação por data é a principal.

    # --- 6. Paginar a lista combinada ---
    paginator = Paginator(combined_list, 12)  # Pagina a lista Python
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- 7. Preparar contexto (formulários) ---
    form = AccountEntryForm()
    installment_form = InstallmentEntryForm()
    transfer_form = TransferForm()

    context = {
        'entries': page_obj.object_list,  # 'entries' agora contém os dicionários
        'form': form,
        'installment_form': installment_form,
        'transfer_form': transfer_form,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'transactions.html', context)


@login_required
def transactions_create(request):
    """
    Processa o formulário de Transação Simples (AccountEntryForm)
    """
    if request.method != 'POST':
        return redirect(reverse('transactions_list'))

    form = AccountEntryForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Transação criada com sucesso.')
        return redirect(reverse('transactions_list'))
    else:
        # Recria o contexto da 'transactions_list' em caso de erro
        # (Nota: esta recriação não terá a lista combinada,
        # é um trade-off para manter a simplicidade na falha do POST)
        qs = AccountEntry.objects.select_related('category', 'account', 'installment_plan').order_by('-competence_date',
                                                                                                     '-date_added')
        paginator = Paginator(qs, 12)
        page_obj = paginator.get_page(1)

        installment_form = InstallmentEntryForm()
        transfer_form = TransferForm()

        context = {
            'entries': page_obj.object_list,  # Lista simples em caso de erro
            'form': form,  # Passa o formulário inválido de volta
            'installment_form': installment_form,
            'transfer_form': transfer_form,
            'is_paginated': page_obj.has_other_pages(),
            'page_obj': page_obj,
        }
        messages.error(request, 'Corrija os erros no formulário de transação simples.')
        return render(request, 'transactions.html', context)


@login_required
def transactions_create_installment(request):
    """
    Processa o formulário de Transação Parcelada (InstallmentEntryForm)
    """
    if request.method != 'POST':
        return redirect(reverse('transactions_list'))

    form = InstallmentEntryForm(request.POST)

    if form.is_valid():
        data = form.cleaned_data

        total_value = data['total_value']
        num_installments = data['number_of_installments']
        first_date = data['first_installment_date']

        try:
            # 1. CRIAR O PLANO MESTRE
            plan = InstallmentPlan.objects.create(
                name=data['describe'],
                total_value=total_value,
                number_of_installments=num_installments,
                account=data['account'],
                category=data['category'],
                first_installment_date=first_date
            )

            # Lógica de cálculo de parcela
            installment_value = (total_value / Decimal(num_installments)).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
            )
            total_calculado = installment_value * (num_installments - 1)
            last_installment_value = total_value - total_calculado

            # 2. LOOP PARA CRIAR AS PARCELAS LIGADAS AO PLANO
            for i in range(num_installments):
                current_date = first_date + relativedelta(months=i)
                current_describe = f"{data['describe']} ({i + 1}/{num_installments})"
                current_value = last_installment_value if (i == num_installments - 1) else installment_value

                AccountEntry.objects.create(
                    category=data['category'],
                    account=data['account'],
                    value=current_value,
                    describe=current_describe,
                    competence_date=current_date,
                    # date_payment fica Nulo por padrão
                    installment_plan=plan,
                    installment_number=(i + 1)
                )

            messages.success(request, f'Plano "{data["describe"]}" ({num_installments} parcelas) criado com sucesso.')

        except Exception as e:
            messages.error(request, f'Erro ao criar parcelas: {e}')

        return redirect(reverse('transactions_list'))

    else:
        # Recria o contexto em caso de erro (lista simples)
        qs = AccountEntry.objects.select_related('category', 'account', 'installment_plan').order_by('-competence_date',
                                                                                                     '-date_added')
        paginator = Paginator(qs, 12)
        page_obj = paginator.get_page(1)

        account_form = AccountEntryForm()
        transfer_form = TransferForm()

        context = {
            'entries': page_obj.object_list,
            'form': account_form,
            'installment_form': form,  # Passa o formulário inválido de volta
            'transfer_form': transfer_form,
            'is_paginated': page_obj.has_other_pages(),
            'page_obj': page_obj,
        }
        messages.error(request, 'Corrija os erros no formulário de parcelamento.')
        return render(request, 'transactions.html', context)


@login_required
def transactions_create_transfer(request):
    """
    Processa o formulário de Transferência (TransferForm)
    """
    if request.method != 'POST':
        return redirect(reverse('transactions_list'))

    form = TransferForm(request.POST)

    if form.is_valid():
        if form.cleaned_data['account_origin'] == form.cleaned_data['account_destination']:
            messages.error(request, 'A conta de origem e destino não podem ser as mesmas.')
        else:
            form.save()
            messages.success(request, 'Transferência registrada com sucesso.')
            return redirect(reverse('transactions_list'))

    # Recria o contexto em caso de erro (lista simples)
    qs = AccountEntry.objects.select_related('category', 'account', 'installment_plan').order_by('-competence_date',
                                                                                                 '-date_added')
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(1)

    account_form = AccountEntryForm()
    installment_form = InstallmentEntryForm()

    context = {
        'entries': page_obj.object_list,
        'form': account_form,
        'installment_form': installment_form,
        'transfer_form': form,  # Passa o formulário inválido de volta
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    if not form.is_valid():
        messages.error(request, 'Corrija os erros no formulário de transferência.')
    return render(request, 'transactions.html', context)


@login_required
def transactions_edit(request, pk):
    """
    Edita UM ÚNICO Lançamento (AccountEntry).
    """
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
    """
    Exclui UM ÚNICO Lançamento (AccountEntry).
    """
    if request.method != 'POST':
        return redirect(reverse('transactions_list'))
    obj = get_object_or_404(AccountEntry, pk=pk)

    if obj.installment_plan:
        messages.error(request,
                       f'Esta é uma parcela. Para excluí-la, remova o plano de parcelamento "{obj.installment_plan.name}" na totalidade.')
        return redirect(reverse('transactions_list'))

    obj.delete()
    messages.success(request, 'Transação excluída.')
    return redirect(reverse('transactions_list'))


@login_required
def installment_plan_edit(request, plan_pk):
    """
    Edita um PLANO de parcelamento e RECRIA as parcelas.
    """
    plan = get_object_or_404(InstallmentPlan, pk=plan_pk)

    if request.method == 'POST':
        form = InstallmentEntryForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # 1. Atualiza o objeto do PLANO
            plan.name = data['describe']
            plan.total_value = data['total_value']
            plan.number_of_installments = data['number_of_installments']
            plan.account = data['account']
            plan.category = data['category']
            plan.first_installment_date = data['first_installment_date']
            plan.save()

            # 2. Lógica de recálculo
            total_value = data['total_value']
            num_installments = data['number_of_installments']
            first_date = data['first_installment_date']

            installment_value = (total_value / Decimal(num_installments)).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
            )
            total_calculado = installment_value * (num_installments - 1)
            last_installment_value = total_value - total_calculado

            # 3. EXCLUI PARCELAS ANTIGAS E RECRIA TODAS
            plan.accountentry_set.all().delete()

            # 4. Recria as parcelas
            for i in range(num_installments):
                current_date = first_date + relativedelta(months=i)
                current_describe = f"{data['describe']} ({i + 1}/{num_installments})"
                current_value = last_installment_value if (i == num_installments - 1) else installment_value

                AccountEntry.objects.create(
                    category=data['category'],
                    account=data['account'],
                    value=current_value,
                    describe=current_describe,
                    competence_date=current_date,
                    # date_payment fica Nulo
                    installment_plan=plan,
                    installment_number=(i + 1)
                )

            messages.success(request, f'Plano "{plan.name}" foi atualizado e parcelas recriadas.')
            return redirect(reverse('transactions_list'))
        else:
            messages.error(request, 'Erro ao atualizar plano. Verifique os campos.')

    else:
        # 5. Preenche o formulário com os dados do PLANO existente
        form_data = {
            'describe': plan.name,
            'total_value': plan.total_value,
            'number_of_installments': plan.number_of_installments,
            'category': plan.category,
            'account': plan.account,
            'first_installment_date': plan.first_installment_date,
        }
        form = InstallmentEntryForm(initial=form_data)

    context = {
        'form': form,
        'plan': plan
    }
    return render(request, 'installment_plan_edit.html', context)


@login_required
def installment_plan_delete(request, plan_pk):
    """
    Exclui um PLANO de parcelamento e todas as parcelas ligadas.
    """
    if request.method != 'POST':
        return redirect(reverse('transactions_list'))

    plan = get_object_or_404(InstallmentPlan, pk=plan_pk)
    plan_name = plan.name
    plan.delete()

    messages.success(request, f'O plano "{plan_name}" e todas as suas parcelas foram excluídos.')
    return redirect(reverse('transactions_list'))


# ===============================================
# NOVAS VIEWS: Para Editar/Excluir Transferências
# ===============================================

@login_required
def transfer_edit(request, pk):
    """
    Edita uma Transferência (Transfer).
    """
    obj = get_object_or_404(Transfer, pk=pk)
    if request.method == 'POST':
        form = TransferForm(request.POST, instance=obj)
        if form.is_valid():
            if form.cleaned_data['account_origin'] == form.cleaned_data['account_destination']:
                messages.error(request, 'A conta de origem e destino não podem ser as mesmas.')
            else:
                form.save()
                messages.success(request, 'Transferência atualizada.')
                return redirect(reverse('transactions_list'))
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = TransferForm(instance=obj)

    # Renderiza um novo template
    return render(request, 'transfer_edit.html', {'form': form, 'transfer': obj})


@login_required
def transfer_delete(request, pk):
    """
    Exclui uma Transferência (Transfer).
    """
    if request.method != 'POST':
        return redirect(reverse('transactions_list'))

    obj = get_object_or_404(Transfer, pk=pk)
    obj.delete()
    messages.success(request, 'Transferência excluída.')
    return redirect(reverse('transactions_list'))


# --- VIEWS DE CATEGORIAS (Sem alterações) ---
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


# --- VIEWS DE CONTAS (Sem alterações) ---
@login_required
def account_list_create(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso.')
            return redirect(reverse('account_list_create') + '?status=active')
        else:
            messages.error(request, 'Erro ao criar conta. Verifique os campos.')
            status_filter = request.GET.get('status', 'active')
    else:
        form = AccountForm()
        status_filter = request.GET.get('status', 'active')

    if status_filter == 'inactive':
        accounts_qs = Account.objects.filter(is_active=False)
    elif status_filter == 'all':
        accounts_qs = Account.objects.all()
    else:
        status_filter = 'active'
        accounts_qs = Account.objects.filter(is_active=True)

    accounts = accounts_qs.order_by('name')

    context = {
        'form': form,
        'accounts': accounts,
        'current_filter': status_filter
    }
    return render(request, 'accounts.html', context)


@login_required
def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk)
    current_filter = request.GET.get('status', 'active')

    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta atualizada com sucesso.')
            redirect_url = reverse('account_list_create') + f'?status={current_filter}'
            return redirect(redirect_url)
        else:
            messages.error(request, 'Erro ao atualizar. Verifique os campos.')
    else:
        form = AccountForm(instance=account)

    context = {
        'form': form,
        'account': account,
        'current_filter': current_filter
    }
    return render(request, 'account_edit.html', context)


@login_required
def account_toggle_active(request, pk):
    if request.method != 'POST':
        return redirect('account_list_create')

    account = get_object_or_404(Account, pk=pk)
    account.is_active = not account.is_active
    account.save()

    action = "reativada" if account.is_active else "inativa"
    messages.success(request, f'Conta "{account.name}" {action} com sucesso.')

    previous_filter = request.POST.get('current_filter', 'active')
    redirect_url = reverse('account_list_create') + f'?status={previous_filter}'
    return redirect(redirect_url)


@login_required
def account_delete(request, pk):
    if request.method != 'POST':
        return redirect('account_list_create')
    account = get_object_or_404(Account, pk=pk)
    try:
        account.delete()
        messages.success(request, 'Conta excluída com sucesso.')
    except ValueError as e:
        messages.error(request,
                       f"Erro: A conta '{account.name}' não pode ser removida, pois há lançamentos ou transferências vinculados a ela.")

    redirect_url = reverse('account_list_create') + '?status=active'
    return redirect(redirect_url)


# --- VIEWS DE METAS (Sem alterações) ---
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