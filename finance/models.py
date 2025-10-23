from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

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
        default='D'  # <--- Tornou-se obrigatório (default Despesa)
    )
    classification = models.CharField(
        max_length=1,
        choices=CLASSIFICATION_CHOICES,
        default='C'  # <--- Tornou-se obrigatório (default C)
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
        default='NA'  # Default "Não Aplicável"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativa")

    def __str__(self):
        status = "" if self.is_active else "Arquivada"
        return f"[{self.get_type_display()}] {self.name}{status}"

class AccountEntry(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)
    date_payment = models.DateTimeField(null=True, blank=True)
    describe = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"[{self.category.get_type_display()}] {self.describe or self.category.name} - R$ {self.value}"

@receiver(pre_delete, sender=Category)
def prevent_delete_if_account_entries_exist(sender, instance, **kwargs):
    if instance.accountentry_set.exists():
        raise ValueError(f"A categoria '{instance.name}' não pode ser removida, pois há lançamentos vinculados a ela.")


class Goal(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nome da Meta")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Alvo (R$)")
    target_date = models.DateField(verbose_name="Data Prevista")

    # Chave estrangeira para a categoria de poupança/investimento associada
    linked_category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # Impedir exclusão da categoria se uma meta depender dela
        verbose_name="Categoria Vinculada (Poupança/Investimento)",
        help_text="Selecione a categoria onde os aportes para esta meta serão registrados.",
        # Limita as opções às categorias do tipo 'INV' (Investimento)
        limit_choices_to={'financial_bucket': 'INV', 'type': 'D'}
    )

    # Campo opcional para notas
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")

    def __str__(self):
        return f"{self.name} (Meta: R$ {self.target_amount})"

    class Meta:
        # Ordenar metas pela data prevista por padrão
        ordering = ['target_date']