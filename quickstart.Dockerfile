FROM ubuntu:20.04

# Exposing ports
EXPOSE 6900

# Environment variables
ENV ARGILLA_LOCAL_AUTH_USERS_DB_FILE=/users.yml
ENV UVICORN_PORT=6900

# Install Python
RUN apt update
RUN apt -y install curl python3.9 python3.9-dev python3.9-distutils gcc gnupg apache2-utils
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py

# Install argilla
RUN pip install argilla[server]

# Install Elasticsearch
RUN curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
RUN echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list
RUN apt update
RUN apt -y install elasticsearch

# Copy users db file along with execution script
COPY scripts/start_quickstart_argilla.sh /
RUN chmod +x /start_quickstart_argilla.sh

# Executing argilla along with elasticsearch
CMD /bin/bash /start_quickstart_argilla.sh
