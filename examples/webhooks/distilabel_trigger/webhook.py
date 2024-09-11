import http
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Literal

import argilla as rg
from argilla._models import RecordModel
from distilabel.steps.tasks import UltraFeedback, Task
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from standardwebhooks.webhooks import WebhookVerificationError

from configure_models import initialize_text_generation_models, initialize_ultrafeedback
from configure_webhook import configure_webhook
from dataset_setup import prepare_dataset

# Environment variables with defaults
API_KEY = os.environ.get("ARGILLA_API_KEY", "argilla.apikey")
API_URL = os.environ.get("ARGILLA_API_URL", "http://localhost:6900")

# Initialize Argilla client
client = rg.Argilla(api_key=API_KEY, api_url=API_URL)

dataset = prepare_dataset(client)
text_generation_models = initialize_text_generation_models()
ultrafeedback = initialize_ultrafeedback()

thread_pool = ThreadPoolExecutor(max_workers=2)
webhook = configure_webhook(client, "/webhook")

server = FastAPI()


@server.middleware("http")
async def webhook_verify(request: Request, call_next):
    try:
        body = await request.body()
        webhook.verify(body, dict(request.headers))
    except WebhookVerificationError as e:
        raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED, detail=str(e))
    else:
        return await call_next(request)


class RecordCompletedEvent(BaseModel):
    type: Literal["record.completed"] = "record.completed"
    timestamp: datetime
    data: RecordModel  # Events work at API Model level, not resource model level


@server.post("/webhook")
async def webhook_handler(body: dict):
    if body["type"] != "record.completed":
        return
    event = RecordCompletedEvent.model_validate(body)
    future = thread_pool.submit(handle_event, event)
    future.result()


def handle_event(event: RecordCompletedEvent) -> None:
    print("Received webhook payload:", event)

    if event.data.dataset_id != dataset.id:
        print("Ignoring webhook payload")
        return

    record = rg.Record.from_model(event.data, dataset=dataset)
    try:
        respond_to_good_instructions(record, text_generation_models, ultrafeedback)
    except Exception as e:
        print("Error processing record", record.id, e)


def respond_to_record(record: rg.Record, models: List[Task]):
    responses = []
    for task in models:
        print(task.name)
        output = list(task.process([{"instruction": record.fields["instruction"]}]))[0][
            0
        ]
        generation = output["generation"]
        responses.append(generation)
    return responses


def add_feedback_suggestions(
    record: rg.Record, response_1, response_2, ultrafeedback: UltraFeedback
) -> None:
    response = ultrafeedback.process(
        [
            {
                "instruction": "trivia questions",
                "generations": [
                    response_1,
                    response_2,
                ],
            }
        ],
    )
    response = list(response)[0][0]
    ratings = response["ratings"]
    rationales = response["rationales"]

    for n, (rating, rationale) in enumerate(zip(ratings, rationales), 1):
        if rating is not None:
            record.suggestions.add(
                suggestion=rg.Suggestion(
                    question_name=f"response{n}_rating",
                    value=rating,
                )
            )
        if rationale is not None:
            record.suggestions.add(
                suggestion=rg.Suggestion(
                    question_name=f"response{n}_rationale",
                    value=rationale,
                )
            )

    for response in record.responses["respond"]:
        response.status = "draft"


def respond_to_good_instructions(
    record: rg.Record, models: List[Task], ultrafeedback: UltraFeedback
) -> None:
    if not record.responses["respond"] or record.responses["respond"][0].value != "yes":
        return

    response_1, response_2 = respond_to_record(record=record, models=models)

    updated_fields = dict(record.fields)
    updated_fields["response1"] = response_1
    updated_fields["response2"] = response_2

    add_feedback_suggestions(
        record=record,
        response_1=response_1,
        response_2=response_2,
        ultrafeedback=ultrafeedback,
    )

    dataset.records.log([record])
