#!/usr/bin/bash
set -e

# Run database migrations
python -m argilla.tasks.database.migrate

# Create default user
if [ "$ADMIN_ENABLED" = "true" ]; then
  python -m argilla.tasks.users.create_default --password $ADMIN_PASSWORD --api-key $ADMIN_API_KEY
fi

# Run argilla-server (See https://www.uvicorn.org/settings/#settings)
#
# From uvicorn docs:
#   You can also configure Uvicorn using environment variables
#   with the prefix UVICORN_. For example, in case you want to
#   run the app on port 5000, just set the environment variable
#   UVICORN_PORT to 5000.
uvicorn argilla:app --host "0.0.0.0"
