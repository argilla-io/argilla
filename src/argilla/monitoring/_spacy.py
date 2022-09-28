#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from argilla import TokenClassificationRecord
from argilla.monitoring.base import BaseMonitor
from argilla.monitoring.types import MissingType

try:
    # Conditional modules
    from spacy.language import Language
    from spacy.tokens import Doc
except ModuleNotFoundError:
    Language = MissingType
    Doc = MissingType


class SpacyNERMonitor(BaseMonitor):
    """A spaCy Language wrapper for NLP NER monitoring in argilla"""

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
            Passed on to the `argilla.TokenClassificationRecord`.

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

    def _prepare_log_data(
        self, docs_info: Tuple[Doc, Optional[Dict[str, Any]]]
    ) -> Dict[str, Any]:

        return dict(
            records=[
                self.doc2token_classification(
                    doc, agent=self.__wrapped__.path.name, metadata=metadata
                )
                for doc, metadata in docs_info
            ],
            name=self.dataset,
            tags={k: v for k, v in self.__model__.meta.items() if isinstance(v, str)},
            metadata=self.__model__.meta,
        )

    def pipe(self, *args, **kwargs):
        as_tuples = kwargs.get("as_tuples")
        results = self.__model__.pipe(*args, **kwargs)

        log_info = []
        for r in results:
            metadata = {}
            if as_tuples:
                doc, metadata = r  # context
            else:
                doc = r
            if self.is_record_accepted():
                log_info.append((doc, metadata))
            yield r

        self.log_async(log_info)

    def __call__(self, *args, **kwargs):
        metadata = kwargs.pop("metadata", None)
        doc = self.__wrapped__(*args, **kwargs)
        try:
            if self.is_record_accepted():
                self.log_async([(doc, metadata)])
        finally:
            return doc


def ner_monitor(nlp: Language, dataset: str, sample_rate: float) -> Language:
    return SpacyNERMonitor(nlp, dataset=dataset, sample_rate=sample_rate)
