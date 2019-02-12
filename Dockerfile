FROM python:3.6.5
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
COPY . /app/
WORKDIR /app/
# Latest version of pipenv, currently broken with default version
RUN pip3 install pipenv==2018.11.26
ADD Pipfile Pipfile
RUN pipenv install --deploy --system
EXPOSE 8000
