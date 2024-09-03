#!/usr/bin/env bash

set -e

# Preset oauth env vars based on injected space variables.
# See https://huggingface.co/docs/hub/en/spaces-oauth#create-an-oauth-app
export OAUTH2_HUGGINGFACE_CLIENT_ID=$OAUTH_CLIENT_ID
export OAUTH2_HUGGINGFACE_CLIENT_SECRET=$OAUTH_CLIENT_SECRET
export OAUTH2_HUGGINGFACE_SCOPE=$OAUTH_SCOPES

# Set the space author name as username if no provided.
# See https://huggingface.co/docs/hub/en/spaces-overview#helper-environment-variables for more details
export USERNAME="${USERNAME:-$SPACE_AUTHOR_NAME}"

honcho start
