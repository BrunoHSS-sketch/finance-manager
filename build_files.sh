#!/bin/bash

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --clear

python manage.py makemigrations
python manage.py migrate --noinput
python manage.py tailwind install
python manage.py collectstatic
python manage.py tailwind start



echo "BUILD FINISHED"
