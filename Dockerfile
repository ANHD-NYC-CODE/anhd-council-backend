FROM python:3.6.5
COPY . /app/
WORKDIR /app/
# Latest version of pipenv, currently broken with default version
RUN pip3 install pipenv==2018.11.26
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --deploy --system
RUN python3.6 manage.py migrate
RUN python 3.6 manage.py collectstatic
EXPOSE 8001
