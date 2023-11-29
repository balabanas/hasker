# Base image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /hasker

# Copy the requirements file
COPY requirements_prod.txt .

# Install dependencies including uwsgi
RUN apt-get update \
    && apt-get install -y netcat-traditional \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libpcre3-dev \
    && pip install --no-cache-dir -r requirements_prod.txt \
    && apt-get purge -y --auto-remove build-essential python3-dev libpcre3-dev \
    && rm -rf /var/lib/apt/lists/*


# copy the project code
COPY . .

# prepare scripts to run
COPY ./basesite/fixtures/install_fixtures.sh .
RUN sed -i 's/\r$//g' entrypoint.sh
RUN sed -i 's/\r$//g' install_fixtures.sh
RUN chmod +x entrypoint.sh
RUN chmod +x install_fixtures.sh

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose the application port
EXPOSE 8080

# Entrypoint: wait for postgres
ENTRYPOINT ["/hasker/entrypoint.sh"]
