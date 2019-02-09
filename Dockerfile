FROM python:3.6.5
COPY . /app/
WORKDIR /app/
# Latest version of pipenv, currently broken with default version
RUN pip3 install pipenv==2018.11.26
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY ./docker-entrypoint.sh docker-entrypoint.sh
RUN pipenv install --deploy --system

EXPOSE 8001
ENTRYPOINT ["docker-entrypoint.sh"]
