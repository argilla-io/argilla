FROM python:3.7

# Copying argilla distribution files
COPY dist/*.whl /packages/

# Copying script for starting argilla server by checking the elasticsearch status
COPY scripts/start_argilla_server.sh /
RUN chmod +x /start_argilla_server.sh

# Environment Variables
ENV USERS_DB=/config/.users.yml

# Downloading wait-for-it script along with installing argilla-server pacakge
RUN wget -O /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
 && chmod +x /wait-for-it.sh \
 && find /packages/*.whl -exec pip install {}[server] \;

# Executing wait-for-it script followed by starting the argilla server
CMD /wait-for-it.sh -t 15 ${ARGILLA_ELASTICSEARCH} -- bash /start_argilla_server.sh
