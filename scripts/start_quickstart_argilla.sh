#!/usr/bin/env bash

set -e

whoami

# Generate hashed passwords
team_password=$(htpasswd -nbB "" "$TEAM_PASSWORD" | cut -d ":" -f 2 | tr -d "\n")
argilla_password=$(htpasswd -nbB "" "$ARGILLA_PASSWORD" | cut -d ":" -f 2 | tr -d "\n")

# Add data to users.yml file
echo "Creating users schema"
cat >"$HOME"/users.yml <<EOF
- username: "team"
  api_key: $TEAM_API_KEY
  full_name: Team
  email: team@argilla.io
  hashed_password: $team_password
  workspaces: []

- username: "argilla"
  api_key: $ARGILLA_API_KEY
  full_name: Argilla
  email: argilla@argilla.io
  hashed_password: $argilla_password
  workspaces: ["team"]
EOF

echo "Starting Elasticsearch"
elasticsearch 1>/dev/null 2>/dev/null &

echo "Waiting for elasticsearch to start"
sleep 30

echo "Running database migrations"
python3.9 -m argilla.tasks.database.migrate

echo "Migrating users to database"
python3.9 -m argilla.tasks.users.migrate || true

# Load data
python3.9 /load_data.py "$TEAM_API_KEY" "$LOAD_DATASETS" &

# Start Argilla
echo "Starting Argilla"
uvicorn argilla:app --host "0.0.0.0"
