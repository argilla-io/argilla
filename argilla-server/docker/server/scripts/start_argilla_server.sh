#!/usr/bin/bash
set -e

# Run database migrations
python -m argilla_server database migrate

# Create default user
if [ "$DEFAULT_USER_ENABLED" = "true" ] || [ "$DEFAULT_USER_ENABLED" = "1" ]; then
	python -m argilla_server database users create_default --password $DEFAULT_USER_PASSWORD --api-key $DEFAULT_USER_API_KEY
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
python -m uvicorn argilla_server:app --host "0.0.0.0"
