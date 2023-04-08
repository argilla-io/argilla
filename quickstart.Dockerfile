FROM docker.elastic.co/elasticsearch/elasticsearch:8.5.3

ENV ADMIN_USERNAME=admin
ENV ADMIN_PASSWORD=12345678
ENV ADMIN_API_KEY=admin.apikey

ENV ANNOTATOR_USERNAME=argilla
ENV ANNOTATOR_PASSWORD=12345678

ENV ARGILLA_WORKSPACE=$ADMIN_USERNAME
ENV LOAD_DATASETS=full
ENV UVICORN_PORT=6900

ENV xpack.security.enabled=false
ENV cluster.routing.allocation.disk.threshold_enabled=false
ENV discovery.type=single-node
ENV ES_JAVA_OPTS=-'Xms512m -Xmx512m'

ENV DEBIAN_FRONTEND=noninteractive

USER root

COPY scripts/start_quickstart_argilla.sh /
COPY scripts/load_data.py /
COPY dist/*.whl /packages/

RUN apt update && \
    apt install -y curl git python3.9 python3.9-dev python3.9-distutils gcc gnupg apache2-utils sudo openssl systemctl && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.9 get-pip.py && \
    pip3 install datasets \
    # Install Argilla
    && chmod +x /start_quickstart_argilla.sh && \
    for wheel in /packages/*.whl; do pip install "$wheel"[server]; done && \
    rm -rf /packages && \
    rm -rf /var/lib/apt/lists/* \
    # This line add context to this image. This solution should be improved
    && echo -e "{  \"deployment\":  \"quickstart\" }" \
    > /usr/local/lib/python3.9/dist-packages/argilla/server/static/deployment.json

USER elasticsearch

CMD ["/start_quickstart_argilla.sh"]
