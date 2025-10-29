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
Parceiro de Programacao
Olá! Claro, vamos criar um excelente ficheiro README.md para o teu projeto "Finance Manager".

Um README é fundamental, pois é o "cartão de visita" do teu projeto. Ele explica o que o projeto faz, por que é útil, quais tecnologias usa e, o mais importante, como outras pessoas o podem instalar e usar.

Com base no ficheiro requirements.txt e nos nomes dos outros ficheiros do projeto, já consigo deduzir bastante sobre ele!

Panorama Geral da Solução
Inferências:

Nome do Projeto: "Finance Manager" (Gestor Financeiro), com base na estrutura de pastas.

Tecnologia Principal: É uma aplicação web feita em Python com o framework Django.

Base de Dados: Utiliza PostgreSQL (indicado por psycopg2-binary), que é uma escolha robusta para produção.

Configuração: Usa python-dotenv para gerir variáveis de ambiente (como chaves de API ou dados da base de dados) e dj-config-url para configurar a ligação à base de dados, provavelmente a partir de uma URL.

Implementação (Deployment): Está preparado para produção, usando whitenoise para servir ficheiros estáticos (CSS, JavaScript, imagens) de forma eficiente.

Funcionalidades (Inferidas pelos ficheiros .html): O projeto parece incluir gestão de Contas, Categorias, Transações, Metas (Goals) e Transações Recorrentes.

Estrutura do README: Vamos criar um README.md com as seguintes secções:

Título do Projeto.

Breve descrição.

Funcionalidades Principais (inferidas).

Tecnologias Utilizadas (baseado no requirements.txt).

Instruções de Instalação e Execução.

Configuração (explicando o .env).

Apresentação do Programa (O Ficheiro README)
Aqui está o código completo para o teu ficheiro README.md. Podes copiar e colar isto num novo ficheiro chamado README.md na raiz do teu projeto (brunohss-sketch/finance-manager/finance-manager-production/).

Markdown
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
