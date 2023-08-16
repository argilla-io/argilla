#!/usr/bin/env bash

set -e

echo "Starting Elasticsearch"
/usr/share/elasticsearch/bin/elasticsearch 1>/dev/null 2>/dev/null &

echo "Waiting for elasticsearch to start"
sleep 30

echo "Running database migrations"
python -m argilla database migrate

echo "Creating owner user"
python -m argilla users create \
	--first-name "Owner" \
	--username "$OWNER_USERNAME" \
	--password "$OWNER_PASSWORD" \
	--api-key "$OWNER_API_KEY" \
	--role owner \
	--workspace "$ARGILLA_WORKSPACE"

echo "Creating admin user"
python -m argilla users create \
	--first-name "Admin" \
	--username "$ADMIN_USERNAME" \
	--password "$ADMIN_PASSWORD" \
	--api-key "$ADMIN_API_KEY" \
	--role admin \
	--workspace "$ARGILLA_WORKSPACE"

echo "Creating annotator user"
python -m argilla users create \
	--first-name "Annotator" \
	--username "$ANNOTATOR_USERNAME" \
	--password "$ANNOTATOR_PASSWORD" \
	--role annotator \
	--workspace "$ARGILLA_WORKSPACE"

# Load data
python /load_data.py "$OWNER_API_KEY" "$LOAD_DATASETS" &

# Start Argilla
echo "Starting Argilla"
if [ -n "$ARGILLA_BASE_URL" ]; then
	uvicorn argilla:app --host "0.0.0.0" --root-path "$ARGILLA_BASE_URL"
else
	uvicorn argilla:app --host "0.0.0.0"
fi
