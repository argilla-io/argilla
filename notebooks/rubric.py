from observe.client import Client, AuthenticatedClient
from observe.models import * 
from observe.api.text_classification import bulk_records
from observe.api.token_classification import bulk_records as bulk_records_ner

import logging


class Rubric:
    def __init__(self):
        self.client = None
    
    def init(self, token, base_url = "https://observe-dev.biome.recogn.ai"):
        client = AuthenticatedClient(
            base_url=base_url, 
            token=token,
            timeout=20
        )
        
        self.client = client
        print(self.client)
        
    def log(self, records, dataset, chunk_size=200, task="textcat"):
        if task == "ner":
            bulk_records_fn = bulk_records_ner
            bulk_cls = TokenClassificationRecordsBulk
        else:
            bulk_records_fn = bulk_records
            bulk_cls = TextClassificationRecordsBulk
            
        if len(records) <= chunk_size:
            response = bulk_records_fn.sync(client=self.client, json_body=bulk_cls(
                name=dataset, 
                records=records
            ))
            print(response)
        else:
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i+chunk_size]
                response = bulk_records_fn.sync(client=self.client, json_body=bulk_cls(
                    name=dataset, 
                    records=chunk
                ))
                print(response)

rubric = Rubric()
    
    
    