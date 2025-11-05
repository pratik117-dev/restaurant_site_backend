#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# if [ "$CREATE_SUPERUSER" = "True" ]; then
#     python manage.py createsuperuser \
#       --email "$DJANGO_SUPERUSER_EMAIL" \
#       --name "$DJANGO_SUPERUSER_NAME" \
#       --no-input
# fi

