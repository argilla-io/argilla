# TODO(gabrielmbmb): update this `Dockerfile` to multi-staged build to reduce the image size
ARG ARGILLA_VERSION=latest
FROM argilla/argilla-server:${ARGILLA_VERSION}

USER root

RUN apt-get update && apt-get install -y \
    apt-transport-https \
    gnupg \
    wget

# Install Elasticsearch signing key
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg

# Add Elasticsearch repository
RUN echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-8.x.list

# Copy Argilla distribution files
COPY scripts/* /
COPY quickstart.requirements.txt /packages/requirements.txt

RUN \
    # Indicate that this is a quickstart deployment
    echo -e "{  \"deployment\":  \"quickstart\" }" > /usr/local/lib/python3.10/site-packages/argilla/server/static/deployment.json && \
    # Create an user to run the Argilla server and Elasticsearch
    useradd -ms /bin/bash argilla && \
    # Create a directory where Elasticsearch and Argilla will store their data
    mkdir /data && \
    # Install Elasticsearch and configure it
    apt-get update && apt-get install -y elasticsearch=8.8.2 && \
    chown -R argilla:argilla /usr/share/elasticsearch /etc/elasticsearch /var/lib/elasticsearch /var/log/elasticsearch && \
    chown argilla:argilla /etc/default/elasticsearch && \
    # Install quickstart image dependencies
    pip install -r /packages/requirements.txt && \
    chmod +x /start_quickstart_argilla.sh && \
    # Give ownership of the data directory to the argilla user
    chown -R argilla:argilla /data && \
    # Clean up
    apt-get remove -y wget gnupg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /packages

COPY config/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml

# echo -e "{  \"deployment\":  \"quickstart\" }" \
# > /usr/local/lmib/python/dist-packages/argilla/server/static/deployment.json

USER argilla

ENV ELASTIC_CONTAINER=true

ENV OWNER_USERNAME=owner
ENV OWNER_PASSWORD=12345678
ENV OWNER_API_KEY=owner.apikey

ENV ADMIN_USERNAME=admin
ENV ADMIN_PASSWORD=12345678
ENV ADMIN_API_KEY=admin.apikey

ENV ANNOTATOR_USERNAME=argilla
ENV ANNOTATOR_PASSWORD=12345678

ENV ARGILLA_HOME_PATH=/data/argilla
ENV ARGILLA_WORKSPACE=$ADMIN_USERNAME
ENV LOAD_DATASETS=full
ENV UVICORN_PORT=6900

ENV ES_JAVA_OPTS=-'Xms512m -Xmx512m'

CMD ["/start_quickstart_argilla.sh"]
