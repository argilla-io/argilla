FROM node:14 as frontend

COPY . /build
<<<<<<< HEAD
=======
COPY .git/ /build/.git/

>>>>>>> 9025f469b860a9de1dec32b7ea3543f4182468e4

WORKDIR /build

RUN scripts/build_frontend.sh

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY --from=frontend /build /build

ENV USERS_DB=/config/.users.yml

WORKDIR /build

<<<<<<< HEAD
RUN pip install -U build \
=======
RUN git log --oneline \
 && pip install -U build \
>>>>>>> 9025f469b860a9de1dec32b7ea3543f4182468e4
 && python -m build \
 && find dist/*.whl -exec pip install {}[server] \;

WORKDIR /app

RUN rm -rf /build

# See <https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#module_name>
ENV MODULE_NAME="rubrix.server.server"
ENV VARIABLE_NAME="app"
