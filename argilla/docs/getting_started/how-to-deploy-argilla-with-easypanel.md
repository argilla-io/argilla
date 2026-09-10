---
description: Deploy Argilla with Easypanel
---

This guide describes how to deploy Argilla using [Easypanel](https://easypanel.io/), a server control panel that can deploy Argilla with one click using its official template, without needing to manually run Docker commands.

1. Open your Easypanel dashboard and create (or open) a project
2. Click **+ Add Service** and choose **Templates**
3. Search for **Argilla** and select it
4. Click **Create** to deploy the service

Easypanel provisions the required PostgreSQL, Redis, and Elasticsearch services automatically and runs the Argilla web and worker containers for you.

See the [official Argilla template on Easypanel](https://easypanel.io/templates/argilla) for more details.
