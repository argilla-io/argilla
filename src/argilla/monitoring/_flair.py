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
from typing import Any, Dict, List, Optional, Tuple, Union

from argilla import TokenClassificationRecord
from argilla.client.models import BulkResponse
from argilla.monitoring.base import BaseMonitor
from argilla.monitoring.types import MissingType

try:
    from flair import __version__ as _flair_version
    from flair.data import Sentence
    from flair.models import SequenceTagger
except ModuleNotFoundError:
    Sentence = MissingType
    SequenceTagger = MissingType
    _flair_version = None


class FlairMonitor(BaseMonitor):
    def _prepare_log_data(
        self, data: List[Tuple[Sentence, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        return dict(
            records=[
                TokenClassificationRecord(
                    text=sentence.to_original_text(),
                    tokens=[token.text for token in sentence.tokens],
                    metadata=meta,
                    prediction_agent=self.agent,
                    event_timestamp=datetime.utcnow(),
                    prediction=[
                        (
                            label.value,
                            label.span.start_pos,
                            label.span.end_pos,
                            label.score,
                        )
                        for label in sentence.get_labels(self.__model__.tag_type)
                    ],
                )
                for sentence, meta in data
            ],
            name=self.dataset,
            tags={**(self.tags or {}), "flair_version": _flair_version},
        )

    def predict(self, sentences: Union[List[Sentence], Sentence], *args, **kwargs):
        metadata = kwargs.pop("metadata", None)
        result = self.__model__.predict(sentences, *args, **kwargs)

        if isinstance(sentences, Sentence):
            sentences = [sentences]

        if not metadata:
            metadata = [{}] * len(sentences)

        filtered_data = [
            (sentence, meta)
            for sentence, meta in zip(sentences, metadata)
            if self.is_record_accepted()
        ]
        if filtered_data:
            self._log_future = self.log_async(filtered_data)

        return result


def flair_monitor(
    pl: SequenceTagger,
    dataset: str,
    sample_rate: float,
) -> Optional[SequenceTagger]:

    return FlairMonitor(pl, dataset=dataset, sample_rate=sample_rate)
