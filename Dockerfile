FROM node:14 as build-deps
COPY frontend /usr/src/app
WORKDIR /usr/src/app
RUN yarn
RUN yarn build

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY . /rubrix

COPY --from=build-deps /usr/src/app/dist /static

ENV USERS_DB=/config/.users.yml
ENV ENABLE_SECURITY=1

RUN git init /rubrix
RUN pip install /rubrix[server]

# See <https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#module_name>
ENV MODULE_NAME="rubric.server.server"
ENV VARIABLE_NAME="app"
