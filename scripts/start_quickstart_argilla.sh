#!/usr/bin/env bash

set -e

# Generating hashed password
hashed_password=$(htpasswd -nbB "" "$USER_PASSWORD" | cut -d ":" -f 2 | tr -d "\n")

# Creating users.yml file
cat >users.yml <<EOF
- username: "admin"
  api_key: $USER_API_KEY
  full_name: Hugging Face
  email: hfdemo@argilla.io
  hashed_password: $hashed_password
  workspaces: []

- username: "argilla"
  api_key: $USER_API_KEY
  full_name: Hugging Face
  email: hfdemo@argilla.io
  hashed_password: $hashed_password
  workspaces: ["admin"]
EOF

# Starting elasticsearch & argilla
service elasticsearch start
echo "Waiting for elasticsearch to start"
sleep 15
uvicorn argilla:app --host "0.0.0.0"
