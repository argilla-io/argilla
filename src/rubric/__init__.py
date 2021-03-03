# -*- coding: utf-8 -*-

from rubric.sdk import Client, AuthenticatedClient
from rubric.sdk.models import *
from rubric.sdk.api.text_classification import bulk_records
import requests
from typing import List, Union, Dict
import logging


_client = None  # Variable to store the client after the init

_LOGGER = logging.getLogger(__name__)   # _LOGGER intialization

def init(url='http://localhost:8000', token=None, timeout=5.0) -> bool:
    """Client setup function.

    Parameters
    ----------
    url : str
        Address from which the API is serving. It will use the default UVICORN address as default
    token : str
        Authentification token. A non-secured logging will be considered the default case.
    timeout : float
        Seconds to considered a connection timeout.

    Returns
    -------
    bool
        True if successful, False otherwise.

    """
    global _client

    if token is None:
        _client = Client(base_url=url, timeout=timeout)
    else:
        _client = AuthenticatedClient(base_url=url, token=token, timeout=timeout)

    try:
        response = requests.get(url=url+'/openapi.json').status_code
    except ConnectionRefusedError:
        _LOGGER.error("Connection Refused: cannot connect to the API")  
        return False

    if response == 401:  # Authentification error
        _LOGGER.error("Connection Refused: authentification error. Try checking your credentials.")
        return False

    elif response == 422:  # TODO: concretar mas el mensaje de error, no lo he visto mucho en acción 
        _LOGGER.error("Validation error: unprocessable entity.")
        return False

    elif response == 200:  # Correct authentification
        return True


def log(records: List[Union[TextClassificationRecord, TokenClassificationRecord]], tags: Dict[str, str], name: str, chunk_size: int = 500) -> BulkResponse:
    """Logging method, stores the records obtined under name and tags

    Parameters
    ----------
    records : List[Union[TextClassificationRecord, TokenClassificationRecord]]
        List of records to store
    tags : str
        Tags, containing information about the experiment, that will be passed along with the records
    name : float
        Name of the project

    Returns
    -------
    bool
        BulkResponse if successful, False otherwise.

    """

    if not name:
        _LOGGER.error("Empty project name has been passed as argument.")
        return False
    
    try:
        record_type = type(records[0])
    except IndexError: 
        _LOGGER.error("Empty record list has been passed as argument.")
        return False
    

    processed = 0
    failed = 0

    chunk_size = 500       #we could make it a parammeter
    MAX_CHUNK_SIZE = 5000

    """Check chunk_size <= length of training dataset not needed, as the Python slice system will adjust
    a bigger-than-possible length to the whole list, having all input in the same chunk.
    However, a desired check can be placed to create a custom chunk_size when that limit is exceeded
    """
    if chunk_size > 5000:
        _LOGGER.warning("The introduced chunk size is noticeably large, timeout erros may ocurr. Consider a chunk size smaller than {MAX_CHUNK_SIZE}")


    #Divided into Text and Token Classification Bulks
    if record_type is TextClassificationRecord:
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i+chunk_size]
            
            response = bulk_records.sync(client=_client, 
                        json_body=TextClassificationRecordsBulk(
                            name=name, 
                            tags=tags,
                            records=chunk
                        ))
            try:
                response = response.to_dict()
            except AttributeError:  #if the response of the API is empty, an Attribute Error will raise as response will be a NoneType
                _LOGGER.error("Connection error: API is not responding. Try checking your connection to the API.")
            processed += response["processed"]
            failed += response["failed"]



    if record_type is TokenClassificationRecord:
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i+chunk_size]
            
            response = bulk_records.sync(client=_client, 
                        json_body=TokenClassificationRecordsBulk(
                            name=name, 
                            tags=tags,
                            records=chunk
                        ))
            
            try:
                response = response.to_dict()
            except AttributeError:  #if the response of the API is empty, an Attribute Error will raise as response will be a NoneType
                _LOGGER.error("Connection error: API is not responding. Try checking your connection to the API.")
            processed += response["processed"]
            failed += response["failed"]

    else:   #Record type is not recognised
        _LOGGER.error("Unknown record type passed as argument.")    
        #TODO: podriamos tener una lista con todos los tipos posibles, y imprimir las posibilidades de records.

        return False

    # Creating a composite BulkResponse with the total processed and failed
    return BulkResponse.from_dict({
        "dataset": name,
        "processed": processed,
        "failed": failed
    })

