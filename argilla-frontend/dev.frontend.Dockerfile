ARG ARGILLA_SERVER_TAG=develop

FROM argilladev/argilla-hf-spaces:${ARGILLA_SERVER_TAG}

USER root

RUN apt-get update && \
    apt-get install -y nodejs npm

USER argilla

WORKDIR /home/argilla/frontend

COPY --chown=argilla:argilla dist ./dist
COPY --chown=argilla:argilla .nuxt ./.nuxt
COPY --chown=argilla:argilla package.json ./package.json
COPY --chown=argilla:argilla nuxt.config.ts ./nuxt.config.ts

# NOTE: Right now this Docker image is using dev.argilla.io as server.
# If we want to use a built-in server in the future to check all functionality we can modify the following Procfile
# content adding ElasticSearch and argilla-server processes.
RUN npm install && \
    echo 'frontend: cd /home/argilla/frontend && HOST=0.0.0.0 PORT=3000 npm run start\n' > /home/argilla/Procfile.frontend

WORKDIR /home/argilla/

EXPOSE 3000
EXPOSE 6900
EXPOSE 9200

CMD ["honcho", "start", "--procfile", "Procfile.frontend"]
