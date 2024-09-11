import os
from typing import List

from distilabel.llms import InferenceEndpointsLLM
from distilabel.steps.tasks import TextGeneration, Task, UltraFeedback

LLAMA_MODEL_ID = os.environ.get(
    "LLAMA_MODEL_ID", "meta-llama/Meta-Llama-3.1-8B-Instruct"
)
GEMMA_MODEL_ID = os.environ.get("GEMMA_MODEL_ID", "google/gemma-1.1-7b-it")
ULTRAFEEDBACK_MODEL_ID = os.environ.get(
    "ULTRAFEEDBACK_MODEL_ID", "meta-llama/Meta-Llama-3.1-70B-Instruct"
)


def initialize_text_generation_models() -> List["Task"]:
    llama31 = TextGeneration(
        name="text-generation",
        llm=InferenceEndpointsLLM(
            model_id=LLAMA_MODEL_ID,
            tokenizer_id=LLAMA_MODEL_ID,
        ),
    )
    llama31.load()

    gemma_tiny = TextGeneration(
        name="text-generation",
        llm=InferenceEndpointsLLM(
            model_id=GEMMA_MODEL_ID,
            tokenizer_id=GEMMA_MODEL_ID,
        ),
    )
    gemma_tiny.load()

    return [llama31, gemma_tiny]


def initialize_ultrafeedback():
    ultrafeedback = UltraFeedback(
        aspect="overall-rating",
        llm=InferenceEndpointsLLM(
            model_id=ULTRAFEEDBACK_MODEL_ID,
            tokenizer_id=ULTRAFEEDBACK_MODEL_ID,
        ),
    )

    ultrafeedback.load()

    return ultrafeedback
