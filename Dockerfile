FROM python:3.5.6
COPY . /app/
WORKDIR /app/
RUN pip install pipenv==2018.11.26
ADD Pipfile Pipfile
RUN pipenv install --deploy --system
# EXPOSE 8000
