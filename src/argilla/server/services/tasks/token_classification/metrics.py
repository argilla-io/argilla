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

from typing import Any, ClassVar, Dict, Iterable, List, Optional, Set, Tuple

from pydantic import BaseModel, Field

from argilla.server.services.metrics import ServiceBaseMetric, ServicePythonMetric
from argilla.server.services.metrics.models import CommonTasksMetrics
from argilla.server.services.search.model import ServiceRecordsQuery
from argilla.server.services.tasks.token_classification.model import (
    EntitySpan,
    ServiceTokenClassificationAnnotation,
    ServiceTokenClassificationRecord,
)
from argilla.utils import SpanUtils


class F1Metric(ServicePythonMetric[ServiceTokenClassificationRecord]):
    """The F1 metric based on entity-level.

    We follow the convention of `CoNLL 2003 <https://aclanthology.org/W03-0419/>`_, where:
    `"precision is the percentage of named entities found by the learning system that are correct.
    Recall is the percentage of named entities present in the corpus that are found by the system.
    A named entity is correct only if it is an exact match (...).”`
    """

    def apply(self, records: Iterable[ServiceTokenClassificationRecord]) -> Dict[str, Any]:
        # store entities per label in dicts
        predicted_entities = {}
        annotated_entities = {}

        # extract entities per label to dicts
        for rec in records:
            if rec.prediction:
                self._add_entities_to_dict(rec.prediction.entities, predicted_entities)
            if rec.annotation:
                self._add_entities_to_dict(rec.annotation.entities, annotated_entities)

        # store precision, recall, and f1 per label
        per_label_metrics = {}

        annotated_total, predicted_total, correct_total = 0, 0, 0
        precision_macro, recall_macro = 0, 0
        for label, annotated in annotated_entities.items():
            predicted = predicted_entities.get(label, set())
            correct = len(annotated & predicted)

            # safe divides are used to cover the 0/0 cases
            precision = self._safe_divide(correct, len(predicted))
            recall = self._safe_divide(correct, len(annotated))
            per_label_metrics.update(
                {
                    f"{label}_precision": precision,
                    f"{label}_recall": recall,
                    f"{label}_f1": self._safe_divide(2 * precision * recall, precision + recall),
                }
            )

            annotated_total += len(annotated)
            predicted_total += len(predicted)
            correct_total += correct

            precision_macro += precision / len(annotated_entities)
            recall_macro += recall / len(annotated_entities)

        # store macro and micro averaged precision, recall and f1
        averaged_metrics = {
            "precision_macro": precision_macro,
            "recall_macro": recall_macro,
            "f1_macro": self._safe_divide(2 * precision_macro * recall_macro, precision_macro + recall_macro),
        }

        precision_micro = self._safe_divide(correct_total, predicted_total)
        recall_micro = self._safe_divide(correct_total, annotated_total)
        averaged_metrics.update(
            {
                "precision_micro": precision_micro,
                "recall_micro": recall_micro,
                "f1_micro": self._safe_divide(2 * precision_micro * recall_micro, precision_micro + recall_micro),
            }
        )

        return {**averaged_metrics, **per_label_metrics}

    @staticmethod
    def _add_entities_to_dict(entities: List[EntitySpan], dictionary: Dict[str, Set[Tuple[int, int]]]):
        """Helper function for the apply method."""
        for ent in entities:
            try:
                dictionary[ent.label].add((ent.start, ent.end))
            except KeyError:
                dictionary[ent.label] = {(ent.start, ent.end)}

    @staticmethod
    def _safe_divide(numerator, denominator):
        """Helper function for the apply method."""
        try:
            return numerator / denominator
        except ZeroDivisionError:
            return 0


class DatasetLabels(ServicePythonMetric):
    id: str = Field("dataset_labels", const=True)
    name: str = Field("The dataset entity labels", const=True)
    records_to_fetch: int = 1500

    shuffle_records: bool = Field(default=True)

    def prepare_query(self, query: ServiceRecordsQuery):
        text = query.query_text or ""
        if text:
            text += " AND "
        text += " (_exists_:annotated_by OR _exists_:predicted_by)"

        query.query_text = text
        return query

    def apply(
        self,
        records: Iterable[ServiceTokenClassificationRecord],
    ) -> Dict[str, Any]:
        ds_labels = set()

        for _ in range(0, self.records_to_fetch):  # Only a few of records will be parsed
            record: ServiceTokenClassificationRecord = next(records, None)
            if record is None:
                break

            if record.annotation:
                ds_labels.update([entity.label for entity in record.annotation.entities])
            if record.prediction:
                ds_labels.update([entity.label for entity in record.prediction.entities])
        return {"labels": ds_labels or []}


class MentionMetrics(BaseModel):
    """Mention metrics model"""

    value: str
    label: str
    score: float = Field(ge=0.0)
    capitalness: Optional[str] = Field(None)


class TokenMetrics(BaseModel):
    """
    Token metrics stored in elasticsearch for token classification

    Attributes
        idx: The token index in sentence
        value: The token textual value
        char_start: The token character start position in sentence
        char_end: The token character end position in sentence
        score: Token score info
        tag: Token tag info. Deprecated: Use metrics.predicted.tags or metrics.annotated.tags instead
        custom: extra token level info
    """

    value: str
    capitalness: Optional[str] = None


class TokenClassificationMetrics(CommonTasksMetrics[ServiceTokenClassificationRecord]):
    """Configured metrics for token classification"""

    @staticmethod
    def density(value: int, sentence_length: int) -> float:
        """Compute the string density over a sentence"""
        return value / sentence_length

    @staticmethod
    def capitalness(value: str) -> Optional[str]:
        """Compute capitalness for a string value"""
        value = value.strip()
        if not value:
            return None
        if value.isupper():
            return "UPPER"
        if value.islower():
            return "LOWER"
        if value[0].isupper():
            return "FIRST"
        if any([c.isupper() for c in value[1:]]):
            return "MIDDLE"
        return None

    @staticmethod
    def mentions_metrics(record: ServiceTokenClassificationRecord, mentions: List[Tuple[str, EntitySpan]]):
        def mention_tokens_length(entity: EntitySpan) -> int:
            """Compute mention tokens length"""
            return len(
                set(
                    [
                        token_idx
                        for i in range(entity.start, entity.end)
                        for token_idx in [record.span_utils.char_to_token_idx.get(i)]
                        if token_idx is not None
                    ]
                )
            )

        return [
            MentionMetrics(
                value=mention,
                label=entity.label,
                score=entity.score,
                capitalness=TokenClassificationMetrics.capitalness(mention),
            )
            for mention, entity in mentions
        ]

    @classmethod
    def build_tokens_metrics(cls, record: ServiceTokenClassificationRecord) -> List[TokenMetrics]:
        return [
            TokenMetrics(value=token_value, capitalness=cls.capitalness(token_value))
            for token_idx, token_value in enumerate(record.tokens)
        ]

    @classmethod
    def record_metrics(cls, record: ServiceTokenClassificationRecord) -> Dict[str, Any]:
        """Compute metrics at record level"""
        base_metrics = super(TokenClassificationMetrics, cls).record_metrics(record)

        tokens_metrics = cls.build_tokens_metrics(record)
        return {
            **base_metrics,
            "tokens": tokens_metrics,
            "predicted": {"mentions": cls.mentions_metrics(record, record.predicted_mentions())},
            "annotated": {"mentions": cls.mentions_metrics(record, record.annotated_mentions())},
        }

    @staticmethod
    def _compute_iob_tags(
        span_utils: SpanUtils,
        annotation: Optional[ServiceTokenClassificationAnnotation],
    ) -> Optional[List[str]]:
        """Helper method to compute IOB tags from entity spans

        Args:
            span_utils: Helper class to perform the computation.
            annotation: Contains the spans from which to compute the IOB tags.

        Returns:
            The IOB tags or None if ``annotation`` is None.
        """
        if annotation is None:
            return None

        spans = [(ent.label, ent.start, ent.end) for ent in annotation.entities]
        return span_utils.to_tags(spans)

    metrics: ClassVar[List[ServiceBaseMetric]] = (
        CommonTasksMetrics.metrics
        + [
            DatasetLabels(),
            F1Metric(
                id="F1",
                name="F1 ServiceBaseMetric based on entity-level",
                description="F1 metrics based on entity-level (averaged and per label), "
                "where only exact matches count (CoNNL 2003).",
            ),
        ]
        + [
            ServiceBaseMetric(
                id="predicted_as",
                name="Predicted labels distribution",
            ),
            ServiceBaseMetric(
                id="annotated_as",
                name="Annotated labels distribution",
            ),
            ServiceBaseMetric(
                id="token_frequency",
                name="Tokens frequency distribution",
            ),
            ServiceBaseMetric(
                id="token_capitalness",
                name="Token capitalness distribution",
                description="Computes capitalization information of tokens",
            ),
            ServiceBaseMetric(
                id="predicted_entity_labels",
                name="Predicted entity labels",
                description="Predicted entity labels distribution",
            ),
            ServiceBaseMetric(
                id="predicted_entity_capitalness",
                name="Mention entity capitalness for predictions",
                description="Computes capitalization information of predicted entity mentions",
            ),
            ServiceBaseMetric(
                id="predicted_mentions_distribution",
                name="Predicted mentions distribution by entity",
                description="Computes predicted mentions distribution against its labels",
            ),
            ServiceBaseMetric(
                id="predicted_top_k_mentions_consistency",
                name="Entity label consistency for predictions",
                description="Computes entity label variability for top-k predicted entity mentions",
            ),
            ServiceBaseMetric(
                id="annotated_entity_labels",
                name="Annotated entity labels",
                description="Annotated Entity labels distribution",
            ),
            ServiceBaseMetric(
                id="annotated_entity_capitalness",
                name="Mention entity capitalness for annotations",
                description="Compute capitalization information of annotated entity mentions",
            ),
            ServiceBaseMetric(
                id="annotated_mentions_distribution",
                name="Annotated mentions distribution by entity",
                description="Computes annotated mentions distribution against its labels",
            ),
            ServiceBaseMetric(
                id="annotated_top_k_mentions_consistency",
                name="Entity label consistency for annotations",
                description="Computes entity label variability for top-k annotated entity mentions",
            ),
            # TODO: Remove in v1.10.0
            ServiceBaseMetric(
                id="tokens_length",
                name="Tokens length",
                description="Computes the text length distribution measured in number of tokens",
            ),
            # TODO: Remove in v1.10.0
            ServiceBaseMetric(
                id="token_length",
                name="Token length distribution",
                description="Computes token length distribution in number of characters",
            ),
            # TODO: Remove in v1.10.0
            ServiceBaseMetric(
                id="predicted_entity_density",
                name="Mention entity density for predictions",
                description="Computes the ratio between the number of all entity tokens and tokens in the text",
            ),
            # TODO: Remove in v1.10.0
            ServiceBaseMetric(
                id="predicted_mention_token_length",
                name="Predicted mention tokens length",
                description="Computes the length of the predicted entity mention measured in number of tokens",
            ),
            # TODO: Remove in v1.10.0
            ServiceBaseMetric(
                id="predicted_mention_char_length",
                name="Predicted mention characters length",
                description="Computes the length of the predicted entity mention measured in number of tokens",
            ),
            # TODO: Remove in v1.10.0
            ServiceBaseMetric(
                id="predicted_tag_consistency",
                name="Token tag consistency for predictions",
                description="Computes token tag variability for top-k predicted tags",
            ),
            # TODO: Remove in v1.10.0
            ServiceBaseMetric(
                id="annotated_entity_density",
                name="Mention entity density for annotations",
                description="Computes the ratio between the number of all entity tokens and tokens in the text",
            ),
            # TODO: Remove in v1.10.0
            ServiceBaseMetric(
                id="annotated_mention_token_length",
                name="Annotated mention tokens length",
                description="Computes the length of the entity mention measured in number of tokens",
            ),
            # TODO: Remove in v1.10.0
            ServiceBaseMetric(
                id="annotated_mention_char_length",
                name="Annotated mention characters length",
                description="Computes the length of the entity mention measured in number of tokens",
            ),
            # TODO: Remove in v1.10.0
            ServiceBaseMetric(
                id="annotated_tag_consistency",
                name="Token tag consistency for annotations",
                description="Computes token tag variability for top-k annotated tags",
            ),
        ]
    )
