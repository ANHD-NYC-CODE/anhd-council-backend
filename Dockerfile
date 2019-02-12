FROM python:3.6.2
COPY . /app/
WORKDIR /app/
# Latest version of pipenv, currently broken with default version
RUN pip install pipenv==2018.11.26
ADD Pipfile Pipfile
RUN pipenv install --deploy --system
EXPOSE 8000
