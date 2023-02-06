FROM docker.elastic.co/elasticsearch/elasticsearch:8.5.3

# Environment variable
ENV ARGILLA_LOCAL_AUTH_USERS_DB_FILE=/usr/share/elasticsearch/users.yml
ENV TEAM_PASSWORD=1234
ENV ARGILLA_PASSWORD=1234
ENV TEAM_API_KEY=team.apikey
ENV ARGILLA_API_KEY=rubrix.apikey
ENV LOAD_DATASETS=full
ENV UVICORN_PORT=6900
ENV xpack.security.enabled=false
ENV cluster.routing.allocation.disk.threshold_enabled=false
ENV discovery.type=single-node
ENV ES_JAVA_OPTS=-'Xms512m -Xmx512m'

USER root

# Install packages
RUN apt update
RUN apt -y install curl python3.9 python3.9-dev python3.9-distutils gcc gnupg apache2-utils sudo openssl systemctl
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py
RUN pip3 install datasets

COPY scripts/start_quickstart_argilla.sh /
RUN chmod +x /start_quickstart_argilla.sh

COPY scripts/load_data.py /
COPY dist/*.whl /packages/

# Install argilla
RUN for wheel in /packages/*.whl; do pip install "$wheel"[server]; done

# This line add context to this image. This solution should be improved
RUN echo -e "{  \"deployment\":  \"quickstart\" }" \
  > /usr/local/lib/python3.9/dist-packages/argilla/server/static/deployment.json


# Create Users schema file
USER elasticsearch
RUN touch "$HOME"/users.yml
RUN chown -R elasticsearch:elasticsearch "$HOME"/users.yml
RUN chmod 777 "$HOME"/users.yml

CMD ["/start_quickstart_argilla.sh"]
