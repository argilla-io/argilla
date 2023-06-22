FROM docker.elastic.co/elasticsearch/elasticsearch:8.5.3

ENV DEBIAN_FRONTEND=noninteractive

USER root

# Create a directory where Elasticsearch and Argilla will store their data
# We will use this directory as a volume to persist data between container restarts (mainly in HF spaces)
RUN mkdir /data
RUN chown -R elasticsearch:elasticsearch /data

COPY scripts/start_quickstart_argilla.sh /
COPY scripts/load_data.py /
COPY quickstart.requirements.txt /packages/requirements.txt
COPY dist/*.whl /packages/

RUN apt update && \
    apt install -y curl git python3.9 python3.9-dev python3.9-distutils gcc gnupg apache2-utils sudo openssl systemctl && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.9 get-pip.py \
    # Install Argilla
    && pip3 install -r /packages/requirements.txt && \
    chmod +x /start_quickstart_argilla.sh && \
    for wheel in /packages/*.whl; do pip install "$wheel"[server]; done && \
    rm -rf /packages && \
    rm -rf /var/lib/apt/lists/* \
    # This line add context to this image. This solution should be improved
    && echo -e "{  \"deployment\":  \"quickstart\" }" \
    > /usr/local/lib/python3.9/dist-packages/argilla/server/static/deployment.json

USER elasticsearch

RUN echo "path.data: /data/elasticsearch" >> /usr/share/elasticsearch/config/elasticsearch.yml

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

ENV xpack.security.enabled=false
ENV cluster.routing.allocation.disk.threshold_enabled=false
ENV discovery.type=single-node
ENV ES_JAVA_OPTS=-'Xms512m -Xmx512m'

CMD ["/start_quickstart_argilla.sh"]
