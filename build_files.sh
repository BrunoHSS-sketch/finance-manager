#!/bin/bash

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --clear

# (Opcional, mas recomendado se quiser começar com o esquema limpo na Vercel)
# Aplicar migrações (cria o schema do banco de dados SQLite na Vercel)
# python manage.py migrate --noinput

# (Opcional: Criar superusuário na Vercel - mais complexo, pode fazer manualmente depois)
# echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'password')" | python manage.py shell

echo "BUILD FINISHED"