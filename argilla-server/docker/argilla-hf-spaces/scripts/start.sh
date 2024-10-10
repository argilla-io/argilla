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

export ARGILLA_BACKUPS_PATH=/data/argilla/backups

if [ ! -d ARGILLA_BACKUPS_PATH ]; then
  echo "Initializing backups folder..."
  mkdir -p ARGILLA_BACKUPS_PATH

  # if exists the db file, copy it to the backup folder and rename it
  if [ -f /data/argilla/argilla.db ]; then
    echo "Found argilla.db file, moving it to the argilla home path..."
    cp /data/argilla/argilla.db $ARGILLA_HOME_PATH || true
  fi

  # if exists the server id file, copy it to the argilla folder
  if [ -f /data/argilla/server_id.dat ]; then
    echo "Found server_id.dat file, moving it to argilla home path..."
    cp /data/argilla/server_id.dat $ARGILLA_HOME_PATH || true
  fi

else
  echo "Backup folder already exists..."
fi

# Copy the backup files to the argilla folder
echo "Restoring files from backup folder..."
python restore_argilla_backup.py

echo "Starting processes..."
honcho start
