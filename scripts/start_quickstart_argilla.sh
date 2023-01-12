#!/usr/bin/env bash

set -e

# Changing user
sudo -S su user

# Checks if password is passed in the env
# if not it will run argilla with default users
if [ -n "$ADMIN_PASSWORD" ] && [ -n "$ARGILLA_PASSWORD" ]; then
  # Generate hashed passwords
  admin_password=$(htpasswd -nbB "" "$ADMIN_PASSWORD" | cut -d ":" -f 2 | tr -d "\n")
  argilla_password=$(htpasswd -nbB "" "$ARGILLA_PASSWORD" | cut -d ":" -f 2 | tr -d "\n")

  # Create users.yml file
  cat >/packages/users.yml <<EOF
- username: "admin"
  api_key: $ADMIN_API_KEY
  full_name: Hugging Face
  email: hfdemo@argilla.io
  hashed_password: $admin_password
  workspaces: []

- username: "argilla"
  api_key: $ARGILLA_API_KEY
  full_name: Hugging Face
  email: hfdemo@argilla.io
  hashed_password: $argilla_password
  workspaces: ["admin"]
EOF
fi

# Disable security in elasticsearch configuration
sudo sed -i "s/xpack.security.enabled: true/xpack.security.enabled: false/g" /etc/elasticsearch/elasticsearch.yml
sudo sed -i "s/cluster.initial_master_nodes/#cluster.initial_master_nodes/g" /etc/elasticsearch/elasticsearch.yml
echo "cluster.routing.allocation.disk.threshold_enabled: false" | sudo tee -a /etc/elasticsearch/elasticsearch.yml

# Create elasticsearch directory and change ownership
sudo mkdir -p /var/run/elasticsearch
sudo chown -R elasticsearch:elasticsearch /var/run/elasticsearch

# Starting elasticsearch
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

# Starting argilla
uvicorn argilla:app --host "0.0.0.0"
