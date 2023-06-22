#!/usr/bin/env bash

set -e

echo "Starting Elasticsearch"
elasticsearch 1>/dev/null 2>/dev/null &

echo "Waiting for elasticsearch to start"
sleep 30

echo "Running database migrations"
python3.9 -m argilla database migrate

echo "Creating owner user"
python3.9 -m argilla users create \
  --first-name "Admin" \
  --username "$ADMIN_USERNAME" \
  --password "$ADMIN_PASSWORD" \
  --api-key "$ADMIN_API_KEY" \
  --role owner \
  --workspace "$ARGILLA_WORKSPACE"

echo "Creating annotator user"
python3.9 -m argilla users create \
  --first-name "Annotator" \
  --username "$ANNOTATOR_USERNAME" \
  --password "$ANNOTATOR_PASSWORD" \
  --role annotator \
  --workspace "$ARGILLA_WORKSPACE"

# Load data
python3.9 /load_data.py "$ADMIN_API_KEY" "$LOAD_DATASETS" &

# Start Argilla
echo "Starting Argilla"
uvicorn argilla:app --host "0.0.0.0"
