# finance/management/commands/generate_recurrences.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta

# Importe os modelos necessários
from finance.models import RecurringTransaction, AccountEntry


class Command(BaseCommand):
    help = 'Gera lançamentos (AccountEntry) a partir de modelos de Transações Recorrentes (RecurringTransaction) que estão pendentes.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        generated_count = 0

        self.stdout.write(f"[{timezone.now()}] Iniciando verificação de recorrências pendentes...")

        # Busca recorrências ativas que deveriam ter gerado algo até hoje
        # e cuja data final (se existir) ainda não passou.
        recurring_transactions = RecurringTransaction.objects.filter(is_active=True)

        for rt in recurring_transactions:
            next_date = rt.calculate_next_due_date()

            # Loop para gerar múltiplas ocorrências se o script ficou inativo por muito tempo
            while next_date and next_date <= today:
                # Verifica se a data final já passou (dupla verificação)
                if rt.end_date and next_date > rt.end_date:
                    break  # Sai do loop while para esta recorrência

                # Verifica se já existe um lançamento EXATAMENTE igual (evita duplicação)
                # Esta verificação é básica, pode ser aprimorada se necessário
                exists = AccountEntry.objects.filter(
                    category=rt.category,
                    account=rt.account,
                    value=rt.value,
                    describe=rt.describe,
                    competence_date=next_date  # Compara com a data de competência
                ).exists()

                if not exists:
                    self.stdout.write(
                        f"  Gerando lançamento para '{rt.describe}' com data de competência {next_date.strftime('%d/%m/%Y')}...")

                    AccountEntry.objects.create(
                        category=rt.category,
                        account=rt.account,
                        value=rt.value,
                        describe=rt.describe,
                        competence_date=next_date,
                        date_payment=None  # Data de pagamento fica em branco por padrão
                        # Campos de parcelamento ficam em branco
                    )
                    generated_count += 1

                    # Atualiza a última data gerada e recalcula a próxima
                    rt.last_generated_date = next_date
                    rt.next_due_date = rt.calculate_next_due_date(from_date=next_date)
                    rt.save(update_fields=['last_generated_date', 'next_due_date'])

                else:
                    self.stdout.write(
                        f"  Lançamento para '{rt.describe}' na data {next_date.strftime('%d/%m/%Y')} já existe. Pulando.")
                    # Mesmo que exista, atualizamos o estado da recorrência para não tentar gerar de novo
                    rt.last_generated_date = next_date
                    rt.next_due_date = rt.calculate_next_due_date(from_date=next_date)
                    # Se next_due_date for None (chegou ao fim), salva. Se não, espera a próxima iteração do while.
                    if rt.next_due_date is None:
                        rt.save(update_fields=['last_generated_date', 'next_due_date'])

                # Calcula a próxima data para continuar o loop while (caso precise gerar mais de uma)
                next_date = rt.calculate_next_due_date(from_date=rt.last_generated_date)

        self.stdout.write(self.style.SUCCESS(
            f"[{timezone.now()}] Verificação concluída. {generated_count} lançamentos recorrentes gerados."))