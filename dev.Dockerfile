FROM node:14 as frontend

COPY . /build
COPY .git/ /build/.git/


WORKDIR /build

RUN scripts/build_frontend.sh

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY --from=frontend /build /build

ENV USERS_DB=/config/.users.yml

WORKDIR /build

RUN git log --oneline \
 && pip install -U build \
 && python -m build \
 && find dist/*.whl -exec pip install {}[server] \;

WORKDIR /app

RUN rm -rf /build \
 && wget -O /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
 && chmod +x /wait-for-it.sh

# See <https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#module_name>
ENV MODULE_NAME="rubrix.server.server"
ENV VARIABLE_NAME="app"

CMD /wait-for-it.sh $ELASTICSEARCH -- /start.sh