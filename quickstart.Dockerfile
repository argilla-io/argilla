FROM python:3.9-slim

# Exposing ports
EXPOSE 6900
EXPOSE 9200

# Environment variables
ENV ARGILLA_LOCAL_AUTH_USERS_DB_FILE=/packages/users.yml
ENV UVICORN_PORT=6900

# Copying argilla distribution files
COPY dist/*.whl /packages/

# Copy execution script
COPY scripts/start_quickstart_argilla.sh /
RUN chmod +x /start_quickstart_argilla.sh

# Install packages
RUN apt update
RUN apt -y install python3.9-dev gcc gnupg apache2-utils systemctl curl sudo vim

# Create new user for starting elasticsearch
RUN useradd -ms /bin/bash user -p "$(openssl passwd -1 ubuntu)"
RUN echo 'user ALL=(ALL)   ALL' >> /etc/sudoers

# Install argilla
RUN chmod +x /start_quickstart_argilla.sh \
 && for wheel in /packages/*.whl; do pip install "$wheel"[server]; done

# Install Elasticsearch
RUN curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
RUN echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-8.x.list
RUN apt update
RUN apt -y install elasticsearch=8.5.3

# Executing argilla along with elasticsearch
CMD /bin/bash /start_quickstart_argilla.sh
