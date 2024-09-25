#!/usr/bin/bash
set -e

# Run database migrations
python -m argilla_server database migrate

if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
  echo "Creating owner user with username ${USERNAME}"
  if [ -n "$API_KEY" ]; then
    python -m argilla_server database users create \
    --first-name "$USERNAME" \
    --username "$USERNAME" \
    --password "$PASSWORD" \
    --api-key "$API_KEY" \
    --role owner
  else
    python -m argilla_server database users create \
    --first-name "$USERNAME" \
    --username "$USERNAME" \
    --password "$PASSWORD" \
    --role owner
  fi
else
  echo "No username and password was provided. Skipping user creation"
fi

# Reindexing data into search engine
if [ "$REINDEX_DATASETS" == "true" ] || [ "$REINDEX_DATASETS" == "1" ]; then
  echo "Reindexing existing datasets"
  python -m argilla_server search-engine reindex
fi

# Run argilla-server (See https://www.uvicorn.org/settings/#settings)
#
# From uvicorn docs:
#   You can also configure Uvicorn using environment variables
#   with the prefix UVICORN_. For example, in case you want to
#   run the app on port 5000, just set the environment variable
#   UVICORN_PORT to 5000.

python -m uvicorn $UVICORN_APP --host "0.0.0.0"
