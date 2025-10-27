from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import date
from decimal import Decimal  # Import necessário


# ===============================================
# MODELO: CONTA (Sem alterações)
# ===============================================
class Account(models.Model):
    """
    Representa uma conta financeira do utilizador (Ex: Carteira, Banco X, Cartão Y)
    """
    name = models.CharField(max_length=100, verbose_name="Nome da Conta")
    TYPE_CHOICES = [
        ('CHECKING', 'Conta Corrente / Carteira'),
        ('SAVINGS', 'Poupança'),
        ('CREDIT_CARD', 'Cartão de Crédito'),
        ('INVESTMENT', 'Investimento'),
        ('OTHER', 'Outro'),
    ]
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='CHECKING',
        verbose_name="Tipo de Conta"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativa")

    def __str__(self):
        status = "" if self.is_active else " (Inativa)"
        return f"{self.name} [{self.get_type_display()}]{status}"

    class Meta:
        ordering = ['name']


# ===============================================
# MODELO: CATEGORIA (Sem alterações)
# ===============================================
class Category(models.Model):
    name = models.CharField(max_length=100)
    TYPE_CHOICES = [
        ('R', 'Receita'),
        ('D', 'Despesa'),
    ]
    CLASSIFICATION_CHOICES = [
        ('A', 'A (Muito Importante)'),
        ('B', 'B (Importante)'),
        ('C', 'C (Não essencial)'),
        ('D', 'D (Outros)'),
    ]

    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default='D'
    )
    classification = models.CharField(
        max_length=1,
        choices=CLASSIFICATION_CHOICES,
        default='C'
    )

    BUCKET_CHOICES = [
        ('ESS', 'Essenciais (Meta 50%)'),
        ('LAZ', 'Lazer / Desejos (Meta 30%)'),
        ('INV', 'Poupança / Investimentos (Meta 20%)'),
        ('NA', 'Não Aplicável (Ex: Receitas)'),
    ]

    financial_bucket = models.CharField(
        max_length=3,
        choices=BUCKET_CHOICES,
        default='NA'
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativa")

    def __str__(self):
        status = "" if self.is_active else "Arquivada"
        return f"[{self.get_type_display()}] {self.name}{status}"

    class Meta:
        ordering = ['type', 'name']


# ===============================================
# MODELO: PLANO DE PARCELAMENTO (Sem alterações nesta etapa)
# (Se ainda não aplicou, pode aplicar agora)
# ===============================================
class InstallmentPlan(models.Model):
    """
    Agrupa múltiplos AccountEntry que pertencem ao mesmo parcelamento.
    """
    name = models.CharField(max_length=150, verbose_name="Nome da Compra")
    total_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    number_of_installments = models.PositiveSmallIntegerField(verbose_name="Número de Parcelas")

    account = models.ForeignKey(Account, on_delete=models.PROTECT, verbose_name="Conta (Cartão)")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Categoria")

    first_installment_date = models.DateField(verbose_name="Data da 1ª Parcela")
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            valor_parcela = self.total_value / Decimal(self.number_of_installments)
        except:
            valor_parcela = 0
        return f"{self.name} ({self.number_of_installments}x de R$ {valor_parcela:.2f})"

    class Meta:
        ordering = ['-first_installment_date']


# ===============================================
# MODELO ATUALIZADO: ACCOUNTENTRY (Lançamento)
# ===============================================
class AccountEntry(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        verbose_name="Conta"
    )

    value = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)  # Data da criação do registo
    competence_date = models.DateField(
        default=date.today,
        verbose_name="Data da Competência"
    )

    # ===============================================
    # CAMPO ADICIONADO: Data do Pagamento (Opcional)
    # ===============================================
    date_payment = models.DateField(
        null=True, blank=True,
        verbose_name="Data do Pagamento (Opcional)",
        help_text="Data que o valor foi debitado/creditado no banco."
    )
    # ===============================================

    describe = models.TextField(null=True, blank=True)

    # ===============================================
    # CAMPOS DO PLANO (Se já os adicionou, mantenha-os)
    # ===============================================
    installment_plan = models.ForeignKey(
        InstallmentPlan,
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Plano de Parcelamento"
    )
    installment_number = models.PositiveSmallIntegerField(
        null=True, blank=True,
        verbose_name="Número da Parcela"
    )

    # ===============================================

    def __str__(self):
        return f"[{self.category.get_type_display()}] {self.describe or self.category.name} - R$ {self.value}"

    class Meta:
        ordering = ['-competence_date', '-date_added']


@receiver(pre_delete, sender=Category)
def prevent_delete_if_account_entries_exist(sender, instance, **kwargs):
    if instance.accountentry_set.exists():
        raise ValueError(f"A categoria '{instance.name}' não pode ser removida, pois há lançamentos vinculados a ela.")


# ===============================================
# MODELO: TRANSFERÊNCIA (Sem alterações)
# ===============================================
class Transfer(models.Model):
    account_origin = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="transfers_out",
        verbose_name="Conta de Origem"
    )
    account_destination = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="transfers_in",
        verbose_name="Conta de Destino"
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor (R$)"
    )
    date = models.DateField(
        default=date.today,
        verbose_name="Data da Transferência"
    )
    describe = models.CharField(
        max_length=200,
        blank=True, null=True,
        verbose_name="Descrição (Opcional)"
    )

    def __str__(self):
        return f"R$ {self.value} de {self.account_origin.name} para {self.account_destination.name}"

    class Meta:
        ordering = ['-date']


# ===============================================
# MODELO: META (Sem alterações)
# ===============================================
class Goal(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nome da Meta")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Alvo (R$)")
    target_date = models.DateField(verbose_name="Data Prevista")

    linked_category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name="Categoria Vinculada (Poupança/Investimento)",
        help_text="Selecione a categoria onde os aportes para esta meta serão registrados.",
        limit_choices_to={'financial_bucket': 'INV', 'type': 'D'}
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")

    def __str__(self):
        return f"{self.name} (Meta: R$ {self.target_amount})"

    class Meta:
        ordering = ['target_date']