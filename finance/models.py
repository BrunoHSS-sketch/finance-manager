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
    name = models.CharField(max_length=100, verbose_name="Nome da Conta")
    TYPE_CHOICES = [
        ('CHECKING', 'Conta Corrente / Carteira'),
        ('SAVINGS', 'Poupança'),
        ('CREDIT_CARD', 'Cartão de Crédito'),
        ('INVESTMENT', 'Investimento'),
        ('OTHER', 'Outro'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='CHECKING', verbose_name="Tipo de Conta")
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
    TYPE_CHOICES = [('R', 'Receita'), ('D', 'Despesa'), ]
    CLASSIFICATION_CHOICES = [('A', 'A (Muito Importante)'), ('B', 'B (Importante)'), ('C', 'C (Não essencial)'),
                              ('D', 'D (Outros)'), ]
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='D')
    classification = models.CharField(max_length=1, choices=CLASSIFICATION_CHOICES, default='C')
    BUCKET_CHOICES = [('ESS', 'Essenciais (Meta 50%)'), ('LAZ', 'Lazer / Desejos (Meta 30%)'),
                      ('INV', 'Poupança / Investimentos (Meta 20%)'), ('NA', 'Não Aplicável (Ex: Receitas)'), ]
    financial_bucket = models.CharField(max_length=3, choices=BUCKET_CHOICES, default='NA')
    is_active = models.BooleanField(default=True, verbose_name="Ativa")

    def __str__(self):
        status = "" if self.is_active else "Arquivada"
        return f"[{self.get_type_display()}] {self.name}{status}"

    class Meta:
        ordering = ['type', 'name']


# ===============================================
# MODELO: PLANO DE PARCELAMENTO (Sem alterações)
# ===============================================
class InstallmentPlan(models.Model):
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
# MODELO: ACCOUNTENTRY (Sem alterações)
# ===============================================
class AccountEntry(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, verbose_name="Conta")
    value = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)
    competence_date = models.DateField(default=date.today, verbose_name="Data da Competência")
    date_payment = models.DateField(null=True, blank=True, verbose_name="Data do Pagamento (Opcional)",
                                    help_text="Data que o valor foi debitado/creditado no banco.")
    describe = models.TextField(null=True, blank=True)
    installment_plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, null=True, blank=True,
                                         verbose_name="Plano de Parcelamento")
    installment_number = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Número da Parcela")

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
    account_origin = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="transfers_out",
                                       verbose_name="Conta de Origem")
    account_destination = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="transfers_in",
                                            verbose_name="Conta de Destino")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")
    date = models.DateField(default=date.today, verbose_name="Data da Transferência")
    describe = models.CharField(max_length=200, blank=True, null=True, verbose_name="Descrição (Opcional)")

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
    linked_category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                        verbose_name="Categoria Vinculada (Poupança/Investimento)",
                                        help_text="Selecione a categoria onde os aportes para esta meta serão registrados.",
                                        limit_choices_to={'financial_bucket': 'INV', 'type': 'D'})
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")

    def __str__(self):
        return f"{self.name} (Meta: R$ {self.target_amount})"

    class Meta:
        ordering = ['target_date']


# ===============================================
# NOVO MODELO: TRANSAÇÃO RECORRENTE
# ===============================================
class RecurringTransaction(models.Model):
    """
    Modelo para definir transações que se repetem periodicamente.
    """
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Categoria")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, verbose_name="Conta")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")
    describe = models.CharField(max_length=200, verbose_name="Descrição")

    FREQUENCY_CHOICES = [
        # ('DAILY', 'Diário'), # Removido Diário para simplicidade inicial
        ('WEEKLY', 'Semanal'),
        ('MONTHLY', 'Mensal'),
        ('YEARLY', 'Anual'),
    ]
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, verbose_name="Frequência")
    start_date = models.DateField(verbose_name="Data de Início")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data Final (Opcional)")

    # Campo interno para controlar a geração
    last_generated_date = models.DateField(null=True, blank=True, editable=False,
                                           help_text="Última data em que um lançamento foi gerado para esta recorrência.")
    next_due_date = models.DateField(null=True, blank=True, editable=False,
                                     help_text="Próxima data prevista para geração.")
    is_active = models.BooleanField(default=True, verbose_name="Ativa")

    def __str__(self):
        status = "" if self.is_active else " (Inativa)"
        end = f" até {self.end_date.strftime('%d/%m/%Y')}" if self.end_date else ""
        return f"{self.describe} ({self.get_frequency_display()}) - R$ {self.value}{end}{status}"

    class Meta:
        ordering = ['start_date', 'describe']
        verbose_name = "Transação Recorrente"
        verbose_name_plural = "Transações Recorrentes"

    # Método para calcular a próxima data (pode ser usado no comando)
    def calculate_next_due_date(self, from_date=None):
        from dateutil.relativedelta import relativedelta

        # Se from_date não for fornecida, começa da start_date ou da última gerada
        current_date = from_date or self.last_generated_date or self.start_date

        if self.frequency == 'WEEKLY':
            next_date = current_date + relativedelta(weeks=1)
        elif self.frequency == 'MONTHLY':
            next_date = current_date + relativedelta(months=1)
        elif self.frequency == 'YEARLY':
            next_date = current_date + relativedelta(years=1)
        else:
            return None  # Frequência desconhecida

        # Garante que a próxima data não ultrapasse a data final, se existir
        if self.end_date and next_date > self.end_date:
            return None

        # Garante que a próxima data seja pelo menos a data de início
        if next_date < self.start_date:
            # Se a data calculada for antes do início, a primeira é a start_date
            if not self.last_generated_date:
                return self.start_date
            else:  # Se já gerou antes, algo está estranho, retorna None
                return None

        return next_date

    def save(self, *args, **kwargs):
        # Atualiza a next_due_date sempre que salvar
        self.next_due_date = self.calculate_next_due_date()
        super().save(*args, **kwargs)