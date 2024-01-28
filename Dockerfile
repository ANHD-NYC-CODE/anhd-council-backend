# OLD VERSION
# FROM python:3.6.14
# COPY . /app/
# WORKDIR /app/
# RUN pip install pipenv==2018.11.26
# ADD Pipfile Pipfile
# RUN pipenv install --deploy --system
# EXPOSE 8000

# NEW VERSION (DOCKERIZED for m1)

# Use the specified base image
FROM python:3.6.14  

# Update and install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    g++ \
    wget \
    libgeos-dev \
    make \
    pkg-config \
    libsqlite3-dev \
    sqlite3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Manually build and install proj 6.2.0
RUN wget https://github.com/OSGeo/PROJ/releases/download/6.2.0/proj-6.2.0.tar.gz \
    && tar xvf proj-6.2.0.tar.gz \
    && cd proj-6.2.0 \
    && ./configure \
    && make \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf proj-6.2.0 proj-6.2.0.tar.gz

# Ensure the system can find the newly installed library
ENV LD_LIBRARY_PATH /usr/local/lib:${LD_LIBRARY_PATH}

# Set a working directory
WORKDIR /app

# Copy your application, its dependencies, and the wheel file
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install cython==0.29.13 pipenv  # Install a specific version of Cython and pipenv


# Then try installing pyproj from the source distribution
COPY pyproj-2.4.0.tar.gz /tmp/
RUN pip install /tmp/pyproj-2.4.0.tar.gz || true

RUN pipenv install --deploy --system
