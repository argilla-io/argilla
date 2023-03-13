FROM python:3.9-slim

# Environment Variables
ENV ARGILLA_HOME_PATH=/var/lib/argilla
ENV USERS_DB=/config/.users.yml
ENV UVICORN_PORT=6900

# Copying script for starting argilla server
COPY scripts/start_argilla_server.sh /

# Copying argilla distribution files
COPY dist/*.whl /packages/

RUN chmod +x /start_argilla_server.sh && \
    for wheel in /packages/*.whl; do pip install "$wheel"[server]; done && \
    rm -rf /packages

# Create argilla volume
RUN mkdir -p "$ARGILLA_HOME_PATH"
VOLUME $ARGILLA_HOME_PATH

# Exposing ports
EXPOSE 6900

CMD /bin/bash /start_argilla_server.sh
