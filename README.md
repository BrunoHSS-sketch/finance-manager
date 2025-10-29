# Finance Manager (Gestor Financeiro)

Um projeto de aplicação web desenvolvido em Django para gestão de finanças pessoais. Permite ao utilizador rastrear despesas, receitas, definir metas e categorizar movimentos financeiros.

## 🚀 Funcionalidades Principais

Este projeto permite a gestão completa das finanças pessoais, incluindo:

* **Dashboard:** Uma visão geral da situação financeira (inferido de `dashboard.html`).
* **Gestão de Contas:** Adicionar e editar diferentes contas (bancárias, carteira, etc.) (inferido de `accounts.html`).
* **Gestão de Categorias:** Criar e gerir categorias para receitas e despesas (inferido de `categories.html`).
* **Registo de Transações:** Adicionar, editar e remover transações financeiras (inferido de `transactions.html`).
* **Transações Recorrentes:** Configurar transações que se repetem automaticamente (ex: salário, aluguer) (inferido de `recurring_transactions.html`).
* **Definição de Metas:** Criar metas de poupança ou de gastos (inferido de `goals.html`).
* **Transferências:** Realizar transferências entre contas (inferido de `transfer_edit.html`).

## 🛠️ Tecnologias Utilizadas

O backend deste projeto é construído em Python e utiliza as seguintes bibliotecas principais (baseado em `requirements.txt`):

* **Framework:** Django
* **Base de Dados:** PostgreSQL (via `psycopg2-binary`)
* **Servidor de Ficheiros Estáticos:** Whitenoise
* **Gestão de Configuração:** Python-dotenv e dj-config-url

## 📋 Instruções de Instalação e Execução

Para executar este projeto localmente, segue estes passos:

**1. Clonar o Repositório:**

```bash
git clone <URL_DO_TEU_REPOSITORIO>
cd finance-manager-production
