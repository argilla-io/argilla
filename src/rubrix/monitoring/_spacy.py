from typing import Any, Dict, Optional

import rubrix as rb
from rubrix import TokenClassificationRecord

# Conditional modules
from rubrix.client.monitoring.base import BaseMonitor

try:
    from spacy import Language
    from spacy.tokens import Doc
except ModuleNotFoundError:
    Language = None
    Doc = None


def doc2token_classification(
    doc: Doc, agent: str, metadata: Optional[Dict[str, Any]]
) -> TokenClassificationRecord:
    """
    Converts a spaCy 2 into a token classification record

    Parameters
    ----------
    doc:
        The spacy doc
    agent:
        Agent to use for the prediction_agent field. Could be the model path or model lang + model version
    metadata:
        Extra metadata linked to Rubrix record

    """
    entities = [(ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]
    return TokenClassificationRecord(
        text=doc.text,
        tokens=[t.text for t in doc],
        metadata=metadata or {},
        prediction_agent=agent,
        prediction=entities,
    )


class _SpacyNERMonitor(BaseMonitor):
    """A spaCy Language wrapper for NLP NER monitoring in Rubrix"""

    async def __log_to_rubrix__(
        self, doc: Doc, metadata: Optional[Dict[str, Any]] = None
    ):
        record = doc2token_classification(
            doc, agent=str(self.__wrapped__.path), metadata=metadata
        )
        rb.log(
            record,
            name=self.dataset,
            tags={k: v for k, v in self.__wrapped__.meta.items() if isinstance(v, str)},
            metadata=self.model.meta,
        )

    def pipe(self, *args, **kwargs):
        as_tuples = kwargs.get("as_tuples")
        results = self.model.pipe(*args, **kwargs)

        for r in results:
            metadata = {}
            if as_tuples:
                doc, metadata = r  # context
            else:
                doc = r
            self.run_separate(self.__log_to_rubrix__(doc, metadata))
            yield r

    def __call__(self, *args, **kwargs):
        metadata = kwargs.pop("metadata", None)
        doc = self.__wrapped__(*args, **kwargs)
        try:
            if self.is_record_accepted():
                self.run_separate(self.__log_to_rubrix__(doc, metadata))
        finally:
            return doc


def ner_monitor(nlp: Language, dataset: str, sample_rate: float) -> Language:
    return _SpacyNERMonitor(nlp, dataset=dataset, sample_rate=sample_rate)
