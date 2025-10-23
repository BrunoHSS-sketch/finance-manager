from django import forms
# ===============================================
# ALTERAÇÃO AQUI: Importar ModelForm diretamente
# ===============================================
from django.forms import ModelForm
# ===============================================

# Importar modelos APÓS as importações do Django
from .models import AccountEntry, Category, Goal

TAILWIND_INPUT_CLASSES = 'mt-1 w-full p-2 bg-gray-700 text-white rounded-md'

# ===============================================
# ALTERAÇÃO AQUI: Usar ModelForm diretamente
# ===============================================
class AccountEntryForm(ModelForm):
# ===============================================
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}),
        label="Categoria"
    )

    class Meta:
        model = AccountEntry
        fields = ['category', 'value', 'date_payment', 'describe']
        widgets = {
            # Usar forms.DateTimeInput etc. continua correto
            'date_payment': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': TAILWIND_INPUT_CLASSES}),
            'value': forms.NumberInput(attrs={'step': '0.01', 'class': TAILWIND_INPUT_CLASSES}),
            'describe': forms.Textarea(attrs={'rows': 3, 'class': TAILWIND_INPUT_CLASSES}),
        }

# ===============================================
# ALTERAÇÃO AQUI: Usar ModelForm diretamente
# ===============================================
class CategoryForm(ModelForm):
# ===============================================
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
# ALTERAÇÃO AQUI: Usar ModelForm diretamente
# ===============================================
class GoalForm(ModelForm):
# ===============================================
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
            'target_amount': forms.NumberInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'step': '0.01', 'placeholder': '0.00'}),
            'target_date': forms.DateInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': TAILWIND_INPUT_CLASSES, 'rows': 3, 'placeholder': 'Detalhes adicionais...'}),
        }