#!/bin/bash
echo "INICIANDO A INSTALAÇÃO DAS DEPENDENCIAS"
pip install -r requirements.txt
echo "FINALIZADO A INSTALAÇÃO DAS DEPENDENCIAS"


echo "INICIANDO A MIGRATION"
python manage.py makemigrations
python manage.py migrate --noinput
echo "FINALIZADO AS MIGRATION"


echo "INICIANDO A INSTALAÇÃO DAS DEPENDENCIAS DO TAILWIND"
python manage.py tailwind install
python manage.py tailwind build
echo "FINALIZADO A INSTALAÇÃO DAS DEPENDENCIAS DO TAILWIND"


echo "INICIANDO A CRIAÇÃO DA PASTA STATICFILES"
mkdir -p /vercel/output/static
cp -r staticfiles_build/* /vercel/output/static/
python manage.py collectstatic --noinput --clear
echo "FINALIZADO A CRIAÇÃO DA PASTA STATICFILES"

echo "Listing contents of /vercel/path0/ (project root in build):"
ls -la /vercel/path0/
echo "Listing contents of /vercel/path0/staticfiles_build/ (if created):"
ls -la /vercel/path0/staticfiles_build/

echo "✅ BUILD FINISHED"
