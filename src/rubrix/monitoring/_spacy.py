from datetime import datetime
from typing import Any, Dict, Optional

import rubrix as rb
from rubrix import TokenClassificationRecord
from rubrix.monitoring.base import BaseMonitor
from rubrix.monitoring.types import MissingType

try:
    # Conditional modules
    from spacy.language import Language
    from spacy.tokens import Doc
except ModuleNotFoundError:
    Language = MissingType
    Doc = MissingType


class SpacyNERMonitor(BaseMonitor):
    """A spaCy Language wrapper for NLP NER monitoring in Rubrix"""

    @staticmethod
    def doc2token_classification(
        doc: Doc, agent: str, metadata: Optional[Dict[str, Any]]
    ) -> TokenClassificationRecord:
        """
        Converts a spaCy `Doc` into a token classification record

        Parameters
        ----------
        doc:
            The spacy doc
        agent:
            Agent to use for the prediction_agent field. Could be the model path or model lang + model version
        metadata:
            Passed on to the `rubrix.TokenClassificationRecord`.

        """
        entities = [(ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]
        return TokenClassificationRecord(
            text=doc.text,
            tokens=[t.text for t in doc],
            metadata=metadata or {},
            prediction_agent=agent,
            prediction=entities,
            event_timestamp=datetime.utcnow(),
        )

    def _log2rubrix(self, doc: Doc, metadata: Optional[Dict[str, Any]] = None):
        record = self.doc2token_classification(
            doc, agent=self.__wrapped__.path.name, metadata=metadata
        )
        rb.log(
            record,
            name=self.dataset,
            tags={k: v for k, v in self.__wrapped__.meta.items() if isinstance(v, str)},
            metadata=self.__model__.meta,
            verbose=False,
        )

    def pipe(self, *args, **kwargs):
        as_tuples = kwargs.get("as_tuples")
        results = self.__model__.pipe(*args, **kwargs)

        for r in results:
            metadata = {}
            if as_tuples:
                doc, metadata = r  # context
            else:
                doc = r
            if self.is_record_accepted():
                self.log_async(doc, metadata)
            yield r

    def __call__(self, *args, **kwargs):
        metadata = kwargs.pop("metadata", None)
        doc = self.__wrapped__(*args, **kwargs)
        try:
            if self.is_record_accepted():
                self.log_async(doc, metadata)
        finally:
            return doc


def ner_monitor(nlp: Language, dataset: str, sample_rate: float) -> Language:
    return SpacyNERMonitor(nlp, dataset=dataset, sample_rate=sample_rate)
