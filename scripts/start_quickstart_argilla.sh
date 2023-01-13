#!/usr/bin/env bash

set -e

# Changing user
sudo -S su user

# Generate hashed passwords
team_password=$(htpasswd -nbB "" "$TEAM_PASSWORD" | cut -d ":" -f 2 | tr -d "\n")
argilla_password=$(htpasswd -nbB "" "$ARGILLA_PASSWORD" | cut -d ":" -f 2 | tr -d "\n")

# Create users.yml file
cat >/packages/users.yml <<EOF
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

# Create elasticsearch directory and change ownership
sudo mkdir -p /var/run/elasticsearch
sudo chown -R elasticsearch:elasticsearch /var/run/elasticsearch

# Start elasticsearch
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

# Load data
if [ "$LOAD_DATA_ENABLE" == "true" ]; then
  python3.9 /load_data.py "$TEAM_API_KEY" &
fi
# Starting argilla
uvicorn argilla:app --host "0.0.0.0"
