# TODO(gabrielmbmb): update this `Dockerfile` to multi-staged build to reduce the image size
ARG ARGILLA_VERSION=latest
ARG ARGILLA_SERVER_IMAGE=argilla/argilla-server
FROM ${ARGILLA_SERVER_IMAGE}:${ARGILLA_VERSION}

USER root

# Copy Argilla distribution files
COPY scripts/start.sh /home/argilla
COPY Procfile /home/argilla
COPY requirements.txt /packages/requirements.txt

RUN apt-get update && \
    apt-get install -y apt-transport-https gnupg wget

# Install Elasticsearch signing key
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
# Add Elasticsearch repository
RUN echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-8.x.list

# Install Redis signing key
RUN wget -qO - https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
# Add Redis repository
RUN apt-get install -y lsb-release
RUN echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/redis.list

RUN \
    # Create a directory where Argilla will store the data
    mkdir /data && \
    apt-get update && \
    # Install Elasticsearch and configure it
    apt-get install -y elasticsearch=8.8.2 && \
    chown -R argilla:argilla /usr/share/elasticsearch /etc/elasticsearch /var/lib/elasticsearch /var/log/elasticsearch && \
    chown argilla:argilla /etc/default/elasticsearch && \
    # Install Redis
    apt-get install -y redis && \
    # Install image dependencies
    pip install -r /packages/requirements.txt && \
    chmod +x /home/argilla/start.sh && \
    chmod +x /home/argilla/start_argilla_server.sh && \
    # Give ownership of the data directory to the argilla user
    chown -R argilla:argilla /data && \
    # Clean up
    apt-get remove -y wget gnupg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /packages

COPY config/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml

USER argilla

# NOTE: We have not found documentation about ELASTIC_CONTAINER environment variable but it could be
# used to indicate that Elasticsearch is running in a container.
# It is used in official Elastic Dockerfiles so we are not removing it for now:
# https://github.com/search?q=repo%3Aelastic%2Fdockerfiles%20ELASTIC_CONTAINER&type=code
ENV ELASTIC_CONTAINER=true
ENV ES_JAVA_OPTS="-Xms1g -Xmx1g"

ENV ARGILLA_HOME_PATH=/data/argilla
ENV BACKGROUND_NUM_WORKERS=2
ENV REINDEX_DATASETS=1

CMD ["/bin/bash", "start.sh"]
