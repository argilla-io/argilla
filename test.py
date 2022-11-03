import pandas as pd
from transformers import pipeline

import argilla as rg

# test text
phrase = (
    "Paris is the capital and most populous city of France, with an estimated"
    " population of 2,175,601 residents as of 2018, in an area of more than 105 square"
    " kilometres (41 square miles). The City of Paris is the centre and seat of"
    " government of the region and province of ÃƒÂŽle-de-France, or Paris Region, which"
    " has an estimated population of 12,174,880, or about 18 percent of the population"
    " of France as of 2017."
)
classifier = pipeline("summarization")

# Get three summaries
predictions = [
    output["summary_text"]
    for output in classifier(phrase, num_return_sequences=3, max_length=56)
]

# Log the records to Argilla
record = [
    rg.Text2TextRecord(
        text=phrase,
        prediction=predictions,
    )
] * 2

rg.DatasetForTextGeneration(record)
