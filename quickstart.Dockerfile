FROM docker.elastic.co/elasticsearch/elasticsearch:8.5.3

# Environment variable
ENV ARGILLA_LOCAL_AUTH_USERS_DB_FILE=/usr/share/elasticsearch/users.yml
ENV TEAM_PASSWORD=1234
ENV ARGILLA_PASSWORD=1234
ENV TEAM_API_KEY=team.apikey
ENV ARGILLA_API_KEY=argilla.apikey
ENV LOAD_DATASETS=full
ENV UVICORN_PORT=6900
ENV xpack.security.enabled=false
ENV cluster.routing.allocation.disk.threshold_enabled=false
ENV discovery.type=single-node
ENV ES_JAVA_OPTS=-'Xms512m -Xmx512m'

# Changing user
USER root

# Copying files and give execute permissions
COPY scripts/load_data.py /
COPY dist/*.whl /packages/
COPY scripts/start_quickstart_argilla.sh /
RUN chmod +x /start_quickstart_argilla.sh

# Install packages
RUN apt update && \
    apt -y install curl python3.9 python3.9-dev python3.9-distutils gcc apache2-utils
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py
RUN pip3 install datasets

# Install argilla
RUN for wheel in /packages/*.whl; do pip3 install "$wheel"[server]; done

# Changing user
USER elasticsearch

# Create Users schema file, set ownership and give permissions
RUN touch "$HOME"/users.yml
RUN chown -R elasticsearch:elasticsearch "$HOME"/users.yml
RUN chmod 777 "$HOME"/users.yml

CMD ["/start_quickstart_argilla.sh"]
