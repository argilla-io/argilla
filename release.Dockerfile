FROM python:3.9

# Exposing ports
EXPOSE 6900

# Copying argilla distribution files
COPY dist/*.whl /packages/

# Environment Variables
ENV USERS_DB=/config/.users.yml
ENV UVICORN_PORT=6900

# Copying script for starting argilla server
COPY scripts/start_argilla_server.sh /

RUN chmod +x /start_argilla_server.sh \
    && for wheel in /packages/*.whl; do pip install "$wheel"[server]; done

CMD /bin/bash /start_argilla_server.sh

