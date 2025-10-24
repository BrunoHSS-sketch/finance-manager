#!/bin/bash

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate --noinput

python manage.py tailwind install
python manage.py tailwind build

mkdir -p /vercel/output/static
cp -r staticfiles_build/* /vercel/output/static/
python manage.py collectstatic --noinput --clear

echo "✅ BUILD FINISHED"
