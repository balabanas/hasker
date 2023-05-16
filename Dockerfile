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
    && apt-get install -y netcat \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libpcre3-dev \
    && pip install --no-cache-dir -r requirements_prod.txt \
    && apt-get purge -y --auto-remove build-essential python3-dev libpcre3-dev \
    && rm -rf /var/lib/apt/lists/*


# copy entrypoint.sh
COPY ./entrypoint.sh .
COPY ./basesite/fixtures/install_fixtures.sh .
RUN sed -i 's/\r$//g' /hasker/entrypoint.sh
RUN sed -i 's/\r$//g' /hasker/install_fixtures.sh
RUN chmod +x /hasker/entrypoint.sh
RUN chmod +x /hasker/install_fixtures.sh

# Copy the project code
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose the application port
EXPOSE 8080

# Start the uWSGI server
#CMD ["uwsgi", "--http", "0.0.0.0:8080", "--module", "hasker.wsgi"]
#CMD ["tail", "-f", "/dev/null"]
ENTRYPOINT ["/hasker/entrypoint.sh"]