FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY dist/*.whl /packages/

ENV USERS_DB=/config/.users.yml

RUN wget -O /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
 && chmod +x /wait-for-it.sh \
 && pip install "elasticsearch==7.13.0" \
 && find /packages/*.whl -exec pip install {}[server] \;

# See <https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#module_name>
ENV MODULE_NAME="rubrix.server.server"
ENV VARIABLE_NAME="app"

CMD /wait-for-it.sh $ELASTICSEARCH -- /start.sh