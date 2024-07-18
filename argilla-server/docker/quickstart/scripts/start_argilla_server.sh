#!/usr/bin/env bash

set -e

# Preset oauth env vars based on injected space variables.
# See https://huggingface.co/docs/hub/en/spaces-oauth#create-an-oauth-app
export OAUTH2_HUGGINGFACE_CLIENT_ID=$OAUTH_CLIENT_ID
export OAUTH2_HUGGINGFACE_CLIENT_SECRET=$OAUTH_CLIENT_SECRET
export OAUTH2_HUGGINGFACE_SCOPE=$OAUTH_SCOPES

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

# Forcing reindex on restart since elasticsearch data could be allocated in a non-persistent volume
echo "Reindexing existing datasets"
python -m argilla_server search-engine reindex

# Start Argilla
echo "Starting Argilla"
python -m uvicorn argilla_server:app --host "0.0.0.0"
