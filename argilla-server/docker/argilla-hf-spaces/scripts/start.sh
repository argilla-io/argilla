#!/usr/bin/env bash

set -e

# Preset oauth env vars based on injected space variables.
# See https://huggingface.co/docs/hub/en/spaces-oauth#create-an-oauth-app
export OAUTH2_HUGGINGFACE_CLIENT_ID=$OAUTH_CLIENT_ID
export OAUTH2_HUGGINGFACE_CLIENT_SECRET=$OAUTH_CLIENT_SECRET
export OAUTH2_HUGGINGFACE_SCOPE=$OAUTH_SCOPES

# Set the space creator name as username if no name is provided, if the user is not found, use the provided space author name
# See https://huggingface.co/docs/hub/en/spaces-overview#helper-environment-variables for more details
DEFAULT_USERNAME=$(curl -L -s https://huggingface.co/api/users/${SPACES_CREATOR_USER_ID}/overview | jq -r '.user' || echo "${SPACE_AUTHOR_NAME}")
export USERNAME="${USERNAME:-$DEFAULT_USERNAME}"

DEFAULT_PASSWORD=$(pwgen -s 16 1)
export PASSWORD="${PASSWORD:-$DEFAULT_PASSWORD}"

if [ ! -d /data/argilla/backup ]; then
  echo "Initializing backup folder..."
  mkdir -p /data/argilla/backup

  # if exists the db file, copy it to the backup folder and rename it
  if [ -f /data/argilla/argilla.db ]; then
    echo "Found argilla.db file, moving it to the backup folder..."
    cp /data/argilla/argilla.db /data/argilla/backup || true
  fi

  # if exists the server id file, copy it to the argilla folder
  if [ -f /data/argilla/server_id.dat ]; then
    echo "Found server_id.dat file, moving it to the backup folder..."
    cp /data/argilla/server_id.dat /data/argilla/backup || true
  fi

else
  echo "Backup folder already exists..."
fi

# Copy the backup files to the argilla folder
echo "Restoring files from backup folder..."
cp -r /data/argilla/backup/* $ARGILLA_HOME_PATH || true

echo "Starting processes..."
honcho start
