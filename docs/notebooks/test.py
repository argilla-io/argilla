from rubric.client import Client, AuthenticatedClient
from rubric import *

def create_record(idx, inputs, label, metadata):
 return TextClassificationRecord.from_dict({
     "idx": idx,
     "inputs": inputs,
     "annotation": {
         "agent": "test",
         "labels": [{"class": label}]
     },
     "metadata": metadata
 })


init()

from datasets import load_dataset
dataset = load_dataset("amazon_reviews_multi", "es")

dataset["validation"][0]

records = []
for record in dataset['validation']:
    records.append(create_record(
        idx=record["product_id"],
        inputs={
            "review_body": record['review_body'],
            "review_title": record['review_title']
        },
        metadata={
            "product_category": record["product_category"],
            "reviewer_id": record["reviewer_id"]
        },
        label=record["stars"]
    ))

tags=TextClassificationRecordsBulkTags.from_dict({ 
                    "type":"sentiment classifier",
                    "lang": "spanish",
                    "description": "Spanish sentiment classifier with `multifield inputs` (title and body)"
                })

#empty_list = []
#log(empty_list, tags, "amazon")

log(records, tags, "amazon")

