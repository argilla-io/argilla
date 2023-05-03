FROM python:3.9-slim

# Environment Variables
ENV ARGILLA_HOME_PATH=/var/lib/argilla
ENV DEFAULT_USER_ENABLED=true
ENV DEFAULT_USER_PASSWORD=1234
ENV DEFAULT_USER_API_KEY=argilla.apikey
ENV USERS_DB=/config/.users.yml
ENV UVICORN_PORT=6900

# Copying script for starting argilla server
COPY scripts/start_argilla_server.sh /

# Copying argilla distribution files
COPY dist/*.whl /packages/

RUN apt-get update && \
    apt-get install -y python-dev libpq-dev gcc && \
    pip install psycopg2 && \
    apt-get remove -y python-dev libpq-dev gcc && \
    chmod +x /start_argilla_server.sh && \
    for wheel in /packages/*.whl; do pip install "$wheel"[server]; done && \
    rm -rf /packages

# Create argilla volume
RUN mkdir -p "$ARGILLA_HOME_PATH"
VOLUME $ARGILLA_HOME_PATH

# Exposing ports
EXPOSE 6900

CMD /bin/bash /start_argilla_server.sh
