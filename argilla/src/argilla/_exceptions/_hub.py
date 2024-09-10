class DatasetsServerException(Exception):
    message: str = "Error connecting to Hugging Face Hub datasets-server API"
