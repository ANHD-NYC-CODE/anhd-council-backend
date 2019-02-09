FROM python:3.6.5
COPY . /app/
WORKDIR /app/
# Latest version of pipenv, currently broken with default version
RUN pip3 install pipenv==2018.11.26
ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock
RUN pipenv install --deploy --system
ADD docker-entrypoint.sh docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["sh", "/var/www/anhd-council-backend/docker-entrypoint.sh"]
