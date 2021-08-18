from fastapi import APIRouter

from .text_classification import api as text_classification
from .token_classification import api as token_classification
from .text2text import api as text2text

router = APIRouter()


for task_api in [text_classification, token_classification, text2text]:
    router.include_router(task_api.router)
