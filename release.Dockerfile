FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY dist/*.whl /packages/

ENV USERS_DB=/config/.users.yml


RUN wget -O /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
 && chmod +x /wait-for-it.sh \
 && find /packages/*.whl -exec pip install {}[server] \;

# See <https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#module_name>
ENV MODULE_NAME="argilla"
ENV VARIABLE_NAME="app"

CMD /wait-for-it.sh ${ARGILLA_ELASTICSEARCH:-${ELASTICSEARCH:-no.elastic.found:9200}} -- /start.sh
