import dataclasses
from typing import Any, Dict, List, Optional

from rubrix.server._helpers import unflatten_dict
from rubrix.server.backend.metrics.base import ElasticsearchMetric, TermsAggregation
from rubrix.server.backend.query_helpers import filters


@dataclasses.dataclass
class DatasetLabelingRulesMetric(ElasticsearchMetric):
    def _build_aggregation(self, queries: List[str]) -> Dict[str, Any]:
        rules_filters = [filters.text_query(rule_query) for rule_query in queries]
        # TODO(@frascuchon): use query helpers
        return {
            "filters": {
                "filters": {
                    "covered_records": filters.boolean_filter(
                        should_filters=rules_filters, minimum_should_match=1
                    ),
                    "annotated_covered_records": filters.boolean_filter(
                        filter_query=filters.exists_field("annotated_as"),
                        should_filters=rules_filters,
                        minimum_should_match=1,
                    ),
                }
            }
        }


@dataclasses.dataclass
class LabelingRulesMetric(ElasticsearchMetric):
    id: str

    def _build_aggregation(
        self, rule_query: str, labels: Optional[List[str]]
    ) -> Dict[str, Any]:

        annotated_records_filter = filters.exists_field("annotated_as")
        rule_query_filter = filters.text_query(rule_query)
        aggr_filters = {
            "covered_records": rule_query_filter,
            "annotated_covered_records": filters.boolean_filter(
                filter_query=annotated_records_filter,
                should_filters=[rule_query_filter],
            ),
        }

        if labels is not None:
            for label in labels:
                rule_label_annotated_filter = filters.term_filter(
                    "annotated_as", value=label
                )
                encoded_label = self._encode_label_name(label)
                aggr_filters.update(
                    {
                        f"{encoded_label}.correct_records": filters.boolean_filter(
                            filter_query=annotated_records_filter,
                            should_filters=[
                                rule_query_filter,
                                rule_label_annotated_filter,
                            ],
                            minimum_should_match=2,
                        ),
                        f"{encoded_label}.incorrect_records": filters.boolean_filter(
                            filter_query=annotated_records_filter,
                            must_query=rule_query_filter,
                            must_not_query=rule_label_annotated_filter,
                        ),
                    }
                )

        # TODO(@frascuchon): User query helpers
        return {"filters": {"filters": aggr_filters}}

    @staticmethod
    def _encode_label_name(label: str) -> str:
        return label.replace(".", "@@@")

    @staticmethod
    def _decode_label_name(label: str) -> str:
        return label.replace("@@@", ".")

    def aggregation_result(self, aggregation_result: Dict[str, Any]) -> Dict[str, Any]:
        if self.id in aggregation_result:
            aggregation_result = aggregation_result[self.id]

        aggregation_result = unflatten_dict(aggregation_result)
        results = {
            "covered_records": aggregation_result.pop("covered_records"),
            "annotated_covered_records": aggregation_result.pop(
                "annotated_covered_records"
            ),
        }

        all_correct = []
        all_incorrect = []
        all_precision = []
        for label, metrics in aggregation_result.items():
            correct = metrics.get("correct_records", 0)
            incorrect = metrics.get("incorrect_records", 0)
            annotated = correct + incorrect
            metrics["annotated"] = annotated
            if annotated > 0:
                precision = correct / annotated
                metrics["precision"] = precision
                all_precision.append(precision)

            all_correct.append(correct)
            all_incorrect.append(incorrect)
            results[self._decode_label_name(label)] = metrics

        results["correct_records"] = sum(all_correct)
        results["incorrect_records"] = sum(all_incorrect)
        if len(all_precision) > 0:
            results["precision"] = sum(all_precision) / len(all_precision)

        return results


METRICS = {
    "predicted_as": TermsAggregation(
        id="predicted_as",
        field="predicted_as",
    ),
    "annotated_as": TermsAggregation(
        id="annotated_as",
        field="annotated_as",
    ),
    "labeling_rule": LabelingRulesMetric(id="labeling_rule"),
    "dataset_labeling_rules": DatasetLabelingRulesMetric(id="dataset_labeling_rules"),
}
