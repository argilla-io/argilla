#!/usr/bin/env bash

set -e

echo "Running database migrations"
python -m argilla_server database migrate

if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
  echo "Creating owner user with username ${USERNAME}"
  python -m argilla_server database users create \
    --first-name "$USERNAME" \
    --username "$USERNAME" \
    --password "$PASSWORD" \
    --role owner
else
  echo "No username and password was provided. Skipping user creation"
fi

# Forcing reindex on restart since elasticsearch data could be allocated in a non-persistent volume
echo "Reindexing existing datasets"
python -m argilla_server search-engine reindex

# Start Argilla
echo "Starting Argilla"
python -m uvicorn argilla_server:app --host "0.0.0.0"
