import { Model } from "@vuex-orm/core";
import { ObservationDataset } from "../Dataset";
import RulesMetric from "./RulesMetric.modelTokenClassification";

export default class Rule extends Model {
  static entity = "rules";

  get id() {
    return this.query;
  }

  static fields() {
    return {
      dataset_id: this.string(null),
      label: this.string(null),
      labeling_function: this.string(null),
      description: this.string(null),
      query: this.string(null),
      author: this.string(null),
      created_at: this.string(null),
      // relationships
      dataset: this.belongsTo(ObservationDataset, "dataset_id"),
      rule_metrics: this.hasOne(RulesMetric, "rule_id"),
    };
  }
}
