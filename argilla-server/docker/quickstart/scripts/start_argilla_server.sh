#!/usr/bin/env bash

set -e

echo "Running database migrations"
python -m argilla_server database migrate

echo "Creating owner user"
python -m argilla_server database users create \
	--first-name "Owner" \
	--username "$OWNER_USERNAME" \
	--password "$OWNER_PASSWORD" \
	--api-key "$OWNER_API_KEY" \
	--role owner \
	--workspace "$ARGILLA_WORKSPACE"

echo "Creating admin user"
python -m argilla_server database users create \
	--first-name "Admin" \
	--username "$ADMIN_USERNAME" \
	--password "$ADMIN_PASSWORD" \
	--api-key "$ADMIN_API_KEY" \
	--role admin \
	--workspace "$ARGILLA_WORKSPACE"

echo "Creating annotator user"
python -m argilla_server database users create \
	--first-name "Annotator" \
	--username "$ANNOTATOR_USERNAME" \
	--password "$ANNOTATOR_PASSWORD" \
	--role annotator \
	--workspace "$ARGILLA_WORKSPACE"

if [ "$REINDEX_DATASETS" == "true" ] || [ "$REINDEX_DATASETS" == "1" ]; then
  echo "Reindexing existing datasets"
  python -m argilla_server search-engine reindex
fi

# Start Argilla
echo "Starting Argilla"
python -m uvicorn argilla_server:app --host "0.0.0.0"
