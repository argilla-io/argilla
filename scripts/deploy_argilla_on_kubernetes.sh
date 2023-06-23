#!/usr/bin/env bash

set -e

# Deploy Elasticsearch
kubectl apply -f k8s/elasticsearch-pvc.yaml
kubectl apply -f k8s/elasticsearch-deployment.yaml
kubectl apply -f k8s/elasticsearch-service.yaml

# Deploy Argilla
kubectl apply -f k8s/argilla-server-deployment.yaml
kubectl apply -f k8s/argilla-server-service.yaml
kubectl apply -f k8s/argilla-server-hpa.yaml
kubectl apply -f k8s/argilla-server-ingress.yaml
