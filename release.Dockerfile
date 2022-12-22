FROM python:3.9-slim

# Exposing ports
EXPOSE 6900

# Copying argilla distribution files
COPY dist/*.whl /packages/

# Environment Variables
ENV USERS_DB=/config/.users.yml
ENV UVICORN_PORT=6900

# Copying script for starting argilla server by checking the elasticsearch status
COPY scripts/start_argilla_server.sh /
COPY scripts/wait-for-it.sh /

RUN chmod +x /start_argilla_server.sh \
 && chmod +x /wait-for-it.sh \
 && for wheel in /packages/*.whl; do pip install "$wheel"[server]; done

# Executing wait-for-it script followed by starting the argilla server
CMD /bin/bash /start_argilla_server.sh

