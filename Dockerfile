FROM python:3.6.5
COPY . /app/
WORKDIR /app/
# Latest version of pipenv, currently broken with default version
RUN pip3 install pipenv==2018.11.26
ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock
RUN pipenv install --deploy --system
ADD ./docker-entrypoint.sh /

EXPOSE 8000
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
