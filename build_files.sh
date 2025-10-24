#!/bin/bash

echo "INICIANDO A INSTALAÇÃO DAS DEPENDENCIAS"
# Use o pip versionado
pip3.12 install -r requirements.txt
echo "FINALIZADO A INSTALAÇÃO DAS DEPENDENCIAS"

echo "INICIANDO A CRIAÇÃO DA PASTA STATICFILES E MIGRACOES"
# Use o python versionado
python3.12 manage.py collectstatic --noinput --clear -v 3
python3.12 manage.py makemigrations --noinput
python3.12 manage.py migrate --noinput
echo "FINALIZADO A CRIAÇÃO DA PASTA STATICFILES E MIGRACOES"

# Se você ainda estiver usando Tailwind via Django (verifique se é necessário no build)
# python3.12 manage.py tailwind install
# python3.12 manage.py tailwind build # Use 'build' em vez de 'start' no build

# Verificações (Opcional, mas útil para depuração)
echo "Listing contents of root:"
ls -la
echo "Listing contents of staticfiles_build:"
ls -la staticfiles_build/

echo "BUILD FINISHED"

# Removi o comando 'cp' e o 'tailwind start' que não fazem sentido no build
