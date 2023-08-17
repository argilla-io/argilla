#!/usr/bin/bash
set -e

# Run database migrations
python -m argilla database migrate

# Create default user
if [ "$DEFAULT_USER_ENABLED" = "true" ]; then
	python -m argilla users create_default --password $DEFAULT_USER_PASSWORD --api-key $DEFAULT_USER_API_KEY
fi

# Run argilla-server (See https://www.uvicorn.org/settings/#settings)
#
# From uvicorn docs:
#   You can also configure Uvicorn using environment variables
#   with the prefix UVICORN_. For example, in case you want to
#   run the app on port 5000, just set the environment variable
#   UVICORN_PORT to 5000.

# Check for ARGILLA_BASE_URL and add --root-path if present
if [ -n "$ARGILLA_BASE_URL" ]; then
	uvicorn argilla:app --host "0.0.0.0" --root-path "$ARGILLA_BASE_URL"
else
	uvicorn argilla:app --host "0.0.0.0"
fi
