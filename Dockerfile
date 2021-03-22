FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY . /rubrix

ENV USERS_DB=/config/.users.yml
ENV ENABLE_SECURITY=1

RUN git init /rubrix
RUN pip install /rubrix[server]

# See <https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#module_name>
ENV MODULE_NAME="rubrix.server.server"
ENV VARIABLE_NAME="app"
