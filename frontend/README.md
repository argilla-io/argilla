# Argilla (UI)

For local development of only the UI, you need to start the normal docker-compose.yml of the project (root folder). Then, start the docker-compose.yml of this folder. This docker-compose is only for local development, as it starts a dev mode that watches the file changes and recompiles. This is not suitable for production environments.

1. `cd argilla`
2. `docker compose up`
3. `cd frontend`
4. `docker compose up`
