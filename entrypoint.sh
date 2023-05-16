#!/bin/bash

echo "Waiting for Postgres..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done

echo "Postgres started"

exec "$@"