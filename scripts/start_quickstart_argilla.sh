#!/usr/bin/env bash

set -e

# Changing user
#sudo -S su user

# Generate hashed passwords
team_password=$(htpasswd -nbB "" "$TEAM_PASSWORD" | cut -d ":" -f 2 | tr -d "\n")
argilla_password=$(htpasswd -nbB "" "$ARGILLA_PASSWORD" | cut -d ":" -f 2 | tr -d "\n")

# Create users.yml file
echo "Creating users schema"
#cat <<EOF | sudo tee -a "$HOME"/app/packages/users.yml
#- username: "team"
#  api_key: TEAM_API_KEY
#  full_name: Team
#  email: team@argilla.io
#  hashed_password: TEAM_PASSWORD
#  workspaces: []
#
#- username: "argilla"
#  api_key: ARGILLA_API_KEY
#  full_name: Argilla
#  email: argilla@argilla.io
#  hashed_password: ARGILLA_PASSWORD
#  workspaces: ["team"]
#EOF

# Update API_KEY & PASSWORD in users.yml file
#sudo sed -i 's,TEAM_PASSWORD,'"$team_password"',g' "$HOME"/app/packages/users.yml
#sudo sed -i 's,ARGILLA_PASSWORD,'"$argilla_password"',g' "$HOME"/app/packages/users.yml
#sudo sed -i 's,TEAM_API_KEY,'"$TEAM_API_KEY"',g' "$HOME"/app/packages/users.yml
#sudo sed -i 's,ARGILLA_API_KEY,'"$ARGILLA_API_KEY"',g' "$HOME"/app/packages/users.yml

# Create elasticsearch directory and change ownership
echo "Creating ES folder"
sudo mkdir -p /var/run/elasticsearch
sudo chown -R elasticsearch:elasticsearch /var/run/elasticsearch

# Start elasticsearch
echo "Starting Elasticsearch"
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

# Load data
if [ "$LOAD_DATA_ENABLE" == "true" ]; then
  echo "Starting to load data"
  python3.9 "$HOME"/app/load_data.py "$TEAM_API_KEY" &
fi

# Starting argilla
echo "Starting Argilla"
uvicorn argilla:app --host "0.0.0.0"
