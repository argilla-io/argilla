FROM python:3.9-slim

# Exposing ports
EXPOSE 6900
EXPOSE 9200

# Environment variables
ENV UVICORN_PORT=6900
ENV TEAM_PASSWORD=1234
ENV ARGILLA_PASSWORD=1234
ENV TEAM_API_KEY=team.apikey
ENV ARGILLA_API_KEY=argilla.apikey
ENV LOAD_DATA_ENABLE=true

# Install packages
RUN apt update
RUN apt -y install python3.9-dev gcc gnupg apache2-utils systemctl curl sudo vim
RUN pip3 install datasets

# Create new user for starting elasticsearch
RUN useradd -m -u 1000 user
RUN echo 'user ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

ENV ARGILLA_LOCAL_AUTH_USERS_DB_FILE=$HOME/app/packages/users.yml

# Copying argilla distribution files
COPY dist/*.whl $HOME/app/packages/

# Copy scripts
COPY scripts/load_data.py $HOME/app/
COPY scripts/start_quickstart_argilla.sh $HOME/app/
RUN sudo chmod +x $HOME/app/start_quickstart_argilla.sh


# Install argilla
RUN for wheel in $HOME/app/packages/*.whl; do pip install "$wheel"[server]; done

# Install Elasticsearch
RUN curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
RUN echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-8.x.list
RUN sudo apt update
RUN sudo apt -y install elasticsearch=8.5.3

RUN sudo sed -i "s/xpack.security.enabled: true/xpack.security.enabled: false/g" /etc/elasticsearch/elasticsearch.yml
RUN sudo sed -i "s/cluster.initial_master_nodes/#cluster.initial_master_nodes/g" /etc/elasticsearch/elasticsearch.yml
RUN sudo sed -i '$ a\cluster.routing.allocation.disk.threshold_enabled: false' /etc/elasticsearch/elasticsearch.yml

# Executing argilla along with elasticsearch
CMD $HOME/app/start_quickstart_argilla.sh
