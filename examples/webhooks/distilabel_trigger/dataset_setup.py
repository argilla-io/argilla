import os
from datetime import datetime

import argilla as rg
from datasets import load_dataset

MAX_RECORDS = int(os.environ.get("MAX_RECORDS", 10))


def prepare_dataset(client) -> rg.Dataset:
    workspace = client.workspaces(name="argilla")
    if workspace is None:
        workspace = rg.Workspace(name="argilla", client=client).create()

    dataset = create_dataset(client, workspace)
    load_and_upload_records(dataset)

    return dataset


def create_dataset(client: rg.Argilla, workspace: rg.Workspace) -> rg.Dataset:
    return rg.Dataset(
        client=client,
        workspace=workspace,
        name=f"triggers_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        settings=rg.Settings(
            fields=[
                rg.TextField("persona"),
                rg.TextField("instruction"),
                rg.TextField("response1"),
                rg.TextField("response2"),
            ],
            questions=[
                rg.LabelQuestion(name="respond", labels=["yes", "no"], required=True),
                rg.TextQuestion(name="improved_instruction", required=False),
                rg.TextQuestion(name="response1_rationale", required=False),
                rg.TextQuestion(name="response2_rationale", required=False),
                rg.RatingQuestion(
                    name="response1_rating", values=[1, 2, 3, 4, 5], required=False
                ),
                rg.RatingQuestion(
                    name="response2_rating", values=[1, 2, 3, 4, 5], required=False
                ),
            ],
        ),
    ).create()


def load_and_upload_records(dataset: rg.Dataset):
    ds = load_dataset("proj-persona/PersonaHub", "instruction")
    records_to_upload = []
    for sample in ds["train"].to_iterable_dataset():
        record = rg.Record(
            fields={
                "persona": sample["input persona"],
                "instruction": sample["synthesized text"],
                "response1": "",
                "response2": "",
            },
            id=str(hash(sample["synthesized text"])),
        )
        records_to_upload.append(record)

        if len(records_to_upload) == MAX_RECORDS:
            break

    dataset.records.log(records=records_to_upload)


# def update_record_fields(record_id, updated_fields):
#     url = f"{API_URL}/api/v1/records/{record_id}"
#     headers = {
#         "accept": "application/json",
#         "X-Argilla-Api-Key": API_KEY,
#         "Content-Type": "application/json",
#     }
#     data = {"fields": updated_fields}
#     response = requests.patch(url, headers=headers, json=data)
#     return response.json()


# def delete_response(response_id):
#     url = f"{API_URL}/api/v1/responses/{response_id}"
#     headers = {
#         "accept": "application/json",
#         "X-Argilla-Api-Key": API_KEY,
#         "Content-Type": "application/json",
#     }
#     response = requests.delete(url, headers=headers)
#     return response.json()
