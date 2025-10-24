#!/bin/bash

# Instalar dependências
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate --noinput

python manage.py tailwind install
python manage.py tailwind build

mkdir -p staticfiles_build
python manage.py collectstatic --noinput --clear

echo "✅ BUILD FINISHED"
