DATASETS_INDEX_NAME = f".rubrix.datasets-v0"
DATASETS_RECORDS_INDEX_NAME = ".rubrix.dataset.{}.records-v0"


DATASETS_INDEX_TEMPLATE = {
    "index_patterns": [DATASETS_INDEX_NAME],
    "settings": {"number_of_shards": 1},
    "mappings": {
        "properties": {
            "tags": {
                "type": "nested",
                "properties": {
                    "key": {"type": "keyword"},
                    "value": {"type": "text"},
                },
            },
            "metadata": {
                "type": "nested",
                "properties": {
                    "key": {"type": "keyword"},
                    "value": {"type": "text"},
                },
            },
        }
    },
}

