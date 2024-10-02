#!/usr/bin/env bash

set -e

# Preset oauth env vars based on injected space variables.
# See https://huggingface.co/docs/hub/en/spaces-oauth#create-an-oauth-app
export OAUTH2_HUGGINGFACE_CLIENT_ID=$OAUTH_CLIENT_ID
export OAUTH2_HUGGINGFACE_CLIENT_SECRET=$OAUTH_CLIENT_SECRET
export OAUTH2_HUGGINGFACE_SCOPE=$OAUTH_SCOPES

# Set the space creator name as username if no name is provided, if the user is not found, use the provided space author name
# See https://huggingface.co/docs/hub/en/spaces-overview#helper-environment-variables for more details
DEFAULT_USERNAME=$(curl -s https://huggingface.co/api/users/${SPACES_CREATOR_USER_ID}/overview | jq -r '.user' || echo "$SPACE_AUTHOR_NAME")
export USERNAME="${USERNAME:-$DEFAULT_USERNAME}"

honcho start
