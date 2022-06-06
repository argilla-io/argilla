from rubrix.server.apis.v0.settings.server import settings

DATASETS_INDEX_NAME = settings.dataset_index_name
DATASETS_RECORDS_INDEX_NAME = settings.dataset_records_index_name


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
