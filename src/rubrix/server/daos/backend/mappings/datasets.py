from rubrix.server.settings import settings

DATASETS_INDEX_NAME = settings.dataset_index_name

# TODO(@frascuchon): Define an mapping definition instead and
#  use it when datasets index is created
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
