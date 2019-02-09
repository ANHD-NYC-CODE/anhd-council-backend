cd /var/www/anhd-council-backend
git pull origin master
pipenv install
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
