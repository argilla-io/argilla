from fastapi import Path

from rubrix._constants import DATASET_NAME_REGEX_PATTERN

DATASET_NAME_PATH_PARAM = Path(
    ..., regex=DATASET_NAME_REGEX_PATTERN, description="The dataset name"
)
