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
````

**2. Criar e Ativar um Ambiente Virtual (Virtual Environment):**

````bash
python -m venv venv
.\venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate
````
**3. Instalar as Dependências:**

````bash
pip install -r requirements.txt
````
**4. Configurar as Variáveis de Ambiente:**

````bash
Ini, TOML
# Chave secreta do Django (gera uma nova, podes usar um gerador online)
SECRET_KEY='A_TUA_CHAVE_SECRETA_SUPER_FORTE'

# Define DEBUG como False em produção
DEBUG=True

# Configuração da Base de Dados (Exemplo para PostgreSQL)
# Formato: postgres://USER:PASSWORD@HOST:PORT/NAME
DATABASE_URL='postgres://user_db:password_db@localhost:5432/finance_db'

# Adiciona outros domínios permitidos se necessário
ALLOWED_HOSTS=127.0.0.1, localhost
````
**5. Executar as Migrações da Base de Dados:**

````bash
python manage.py migrate
````
**6. (Opcional) Criar um Super-utilizador:**

````bash
python manage.py createsuperuser
````
**7. Executar o Servidor de Desenvolvimento:**

````bash
python manage.py runserver
````
