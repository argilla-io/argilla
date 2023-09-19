FROM python:3.10

RUN pip install --no-cache-dir slack-sdk==3.21.3

COPY ./app /app

CMD ["python", "/app/main.py"]
