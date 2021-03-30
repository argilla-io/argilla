import datetime

from pydantic.dataclasses import dataclass


@dataclass
class DatasetSnapshot:
    """The dataset snapshot info"""

    id: str
    task: str
    creation_date: datetime.datetime
