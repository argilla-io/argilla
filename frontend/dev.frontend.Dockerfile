ARG ARGILLA_SERVER_TAG=main

FROM argilla/argilla-quickstart:${ARGILLA_SERVER_TAG}

USER root

RUN apt-get update && \
    apt-get install -y nodejs npm

USER argilla

WORKDIR /home/argilla/frontend

COPY --chown=argilla:argilla dist ./dist
COPY --chown=argilla:argilla .nuxt ./.nuxt
COPY --chown=argilla:argilla package.json ./package.json
COPY --chown=argilla:argilla nuxt.config.ts ./nuxt.config.ts

RUN npm install && \
echo \
'elastic: /usr/share/elasticsearch/bin/elasticsearch\n\
argilla: /bin/bash /home/argilla/start_argilla_server.sh\n\
frontend: cd /home/argilla/frontend && HOST=0.0.0.0 PORT=3000 npm run start\n' > /home/argilla/Procfile.frontend

WORKDIR /home/argilla/

EXPOSE 3000
EXPOSE 6900
EXPOSE 9200

CMD ["honcho", "start", "--procfile", "Procfile.frontend"]
