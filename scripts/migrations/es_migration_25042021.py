from itertools import zip_longest
from typing import Any, Dict, List, Optional

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, bulk
from pydantic import BaseSettings
from rubrix.server.tasks.commons import TaskType


class Settings(BaseSettings):
    """
    Migration argument settings
    """

    elasticsearch: str = "http://localhost:9200"
    migration_datasets: List[str] = []
    chunk_size: int = 1000
    task: TaskType


settings = Settings()


source_datasets_index = ".rubric.datasets-v1"
target_datasets_index = ".rubrix.datasets-v0"
source_record_index_pattern = ".rubric.dataset.{}.records-v1"
target_record_index_pattern = ".rubrix.dataset.{}.records-v0"


def batcher(iterable, n, fillvalue=None):
    "batches an iterable"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def map_doc_2_action(
    index: str, doc: Dict[str, Any], task: TaskType
) -> Optional[Dict[str, Any]]:
    """Configures bulk action"""
    doc_data = doc["_source"]
    new_record = {
        "id": doc_data["id"],
        "metadata": doc_data.get("metadata"),
        "last_updated": doc_data.get("last_updated"),
        "words": doc_data.get("words"),
    }

    task_info = doc_data["tasks"].get(task)
    if task_info is None:
        return None

    new_record.update(
        {
            "status": task_info.get("status"),
            "prediction": task_info.get("prediction"),
            "annotation": task_info.get("annotation"),
            "event_timestamp": task_info.get("event_timestamp"),
            "predicted": task_info.get("predicted"),
            "annotated_as": task_info.get("annotated_as"),
            "predicted_as": task_info.get("predicted_as"),
            "annotated_by": task_info.get("annotated_by"),
            "predicted_by": task_info.get("predicted_by"),
            "score": task_info.get("confidences"),
            "owner": task_info.get("owner"),
        }
    )

    if task == TaskType.text_classification:
        new_record.update(
            {
                "inputs": doc_data.get("text"),
                "multi_label": task_info.get("multi_label"),
                "explanation": task_info.get("explanation"),
            }
        )
    elif task == TaskType.token_classification:
        new_record.update(
            {
                "tokens": doc_data.get("tokens"),
                "text": doc_data.get("raw_text"),
            }
        )
    return {
        "_op_type": "index",
        "_index": index,
        "_id": doc["_id"],
        **new_record,
    }


if __name__ == "__main__":

    client = Elasticsearch(hosts=settings.elasticsearch)

    for dataset in settings.migration_datasets:
        source_index = source_record_index_pattern.format(dataset)
        source_index_info = client.get(index=source_datasets_index, id=dataset)

        target_dataset_name = f"{dataset}-{settings.task}".lower()
        target_index = target_record_index_pattern.format(
            target_dataset_name
        )

        target_index_info = source_index_info["_source"]
        target_index_info["task"] = settings.task
        target_index_info["name"] = target_dataset_name

        client.index(
            index=target_datasets_index,
            id=target_index_info["name"],
            body=target_index_info,
        )

        index_docs = scan(client, index=source_index)
        for batch in batcher(index_docs, n=settings.chunk_size):
            bulk(
                client,
                actions=(
                    map_doc_2_action(index=target_index, doc=doc, task=settings.task)
                    for doc in batch
                    if doc is not None
                ),
            )
