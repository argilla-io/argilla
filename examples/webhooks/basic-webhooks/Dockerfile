# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.10

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
COPY --chown=user ./main.py main.py
COPY --chown=user ./start.sh start.sh

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["/bin/sh", "start.sh"]
