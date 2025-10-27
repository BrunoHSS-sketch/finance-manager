from django import forms
from django.forms import ModelForm
from datetime import date

# ===============================================
# IMPORT ADICIONADO: Account, Transfer, InstallmentPlan
# ===============================================
from .models import AccountEntry, Category, Goal, Account, Transfer, InstallmentPlan

TAILWIND_INPUT_CLASSES = 'mt-1 w-full p-2 bg-gray-700 text-white rounded-md'


# ===============================================
# FORMULÁRIO ATUALIZADO: AccountEntryForm
# ===============================================
class AccountEntryForm(ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
        label="Categoria"
    )
    account = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
        label="Conta"
    )

    class Meta:
        model = AccountEntry
        # ===============================================
        # CAMPO ADICIONADO: date_payment
        # ===============================================
        fields = ['category', 'account', 'value', 'competence_date', 'date_payment', 'describe']
        widgets = {
            'competence_date': forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_CLASSES}),
            # ===============================================
            # WIDGET ADICIONADO: date_payment
            # ===============================================
            'date_payment': forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_CLASSES}),
            'value': forms.NumberInput(attrs={'step': '0.01', 'class': TAILWIND_INPUT_CLASSES}),
            'describe': forms.Textarea(attrs={'rows': 3, 'class': TAILWIND_INPUT_CLASSES}),
        }
        labels = {
            'value': 'Valor (R$)',
            'competence_date': 'Data da Competência',
            'date_payment': 'Data do Pagamento (Opcional)',  # <--- LABEL ADICIONADA
            'describe': 'Descrição'
        }


# ===============================================
# FORMULÁRIO: CategoryForm (Sem alterações)
# ===============================================
class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'classification', 'financial_bucket']
        widgets = {
            'name': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'placeholder': 'Ex: Supermercado'}),
            'type': forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
            'classification': forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
            'financial_bucket': forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
        }
        labels = {
            'name': 'Nome da Categoria',
            'type': 'Tipo',
            'classification': 'Classificação (Prioridade)',
            'financial_bucket': 'Balde Orçamentário (50/30/20)'
        }


# ===============================================
# FORMULÁRIO: AccountForm (Sem alterações)
# ===============================================
class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'placeholder': 'Ex: Carteira, Banco X'}),
            'type': forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
        }
        labels = {
            'name': 'Nome da Conta',
            'type': 'Tipo de Conta'
        }


# ===============================================
# FORMULÁRIO: TransferForm (Sem alterações)
# ===============================================
class TransferForm(ModelForm):
    account_origin = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
        label="Conta de Origem"
    )
    account_destination = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
        label="Conta de Destino"
    )

    class Meta:
        model = Transfer
        fields = ['account_origin', 'account_destination', 'value', 'date', 'describe']
        widgets = {
            'value': forms.NumberInput(attrs={'step': '0.01', 'class': TAILWIND_INPUT_CLASSES}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_CLASSES}),
            'describe': forms.TextInput(
                attrs={'class': TAILWIND_INPUT_CLASSES, 'placeholder': 'Ex: Pagamento fatura cartão'}),
        }


# ===============================================
# FORMULÁRIO: InstallmentEntryForm (Sem alterações)
# ===============================================
class InstallmentEntryForm(forms.Form):
    """
    Formulário não-Model para criar uma despesa parcelada.
    """
    describe = forms.CharField(
        label="Descrição da Compra",
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'placeholder': 'Ex: Monitor Novo'})
    )
    total_value = forms.DecimalField(
        label="Valor Total da Compra (R$)",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': TAILWIND_INPUT_CLASSES})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True, type='D'),  # Apenas Despesas
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
        label="Categoria"
    )
    account = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True, type='CREDIT_CARD'),  # Apenas Cartões
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
        label="Conta (Cartão de Crédito)"
    )
    first_installment_date = forms.DateField(
        label="Data da Primeira Parcela",
        widget=forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_CLASSES}),
        initial=date.today
    )
    number_of_installments = forms.IntegerField(
        label="Número de Parcelas",
        min_value=2,
        max_value=48,
        initial=2,
        widget=forms.NumberInput(attrs={'type': 'number', 'class': TAILWIND_INPUT_CLASSES})
    )


# ===============================================
# FORMULÁRIO: GoalForm (Sem alterações)
# ===============================================
class GoalForm(ModelForm):
    linked_category = forms.ModelChoiceField(
        queryset=Category.objects.filter(
            financial_bucket='INV',
            type='D',
            is_active=True
        ),
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
        label="Categoria Vinculada (Poupança/Investimento)",
        help_text="Selecione a categoria ativa onde os aportes serão registrados."
    )

    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'target_date', 'linked_category', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'placeholder': 'Ex: Viagem ao Japão'}),
            'target_amount': forms.NumberInput(
                attrs={'class': TAILWIND_INPUT_CLASSES, 'step': '0.01', 'placeholder': '0.00'}),
            'target_date': forms.DateInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'type': 'date'}),
            'notes': forms.Textarea(
                attrs={'class': TAILWIND_INPUT_CLASSES, 'rows': 3, 'placeholder': 'Detalhes adicionais...'}),
        }