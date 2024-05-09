# Use Python 3.12 as the final base image - 4/2/2024
FROM python:3.12
WORKDIR /app/
COPY Pipfile Pipfile.lock /app/
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install pipenv==2023.10.24 && \
    pipenv install --deploy --system
COPY . /app/
EXPOSE 8000

# FROM python:3.12

# # Set work directory
# WORKDIR /app/

# # Set environment variables
# ENV PIP_ROOT_USER_ACTION=ignore
# ENV DEBIAN_FRONTEND=noninteractive

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     python3-dev \
#     libffi-dev \
#     libssl-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Upgrade pip and install Python dependencies
# RUN pip install --upgrade pip setuptools wheel
# RUN pip install pipenv gunicorn

# # Use the latest versions of gevent and greenlet directly from their repositories
# RUN pip install git+https://github.com/gevent/gevent.git#egg=gevent
# RUN pip install git+https://github.com/python-greenlet/greenlet.git#egg=greenlet

# # Copy the Pipfile and Pipfile.lock into the container
# COPY Pipfile Pipfile.lock /app/

# # Install project dependencies
# RUN pipenv install --deploy --system

# # Copy project
# COPY . /app/

# # Expose port
# EXPOSE 8000
