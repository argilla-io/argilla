from pydantic import BaseModel


class BulkResponse(BaseModel):
    """
    Data info for bulk results

    Attributes
    ----------

    dataset:
        The dataset name
    processed:
        Number of records in bulk
    failed:
        Number of failed records
    """

    dataset: str
    processed: int
    failed: int = 0
