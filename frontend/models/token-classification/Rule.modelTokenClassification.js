import { Model } from "@vuex-orm/core";
import { ObservationDataset } from "../Dataset";
import RulesMetric from "./RulesMetric.modelTokenClassification";

export default class Rule extends Model {
  static entity = "rules";
  static primaryKey = ["query", "author", "name"];

  // get id() {
  //   return [this.query, ...this.dataset_id];
  // }

  static fields() {
    return {
      id: this.uid(),
      dataset_id: this.attr(null),
      label: this.string(null),
      labeling_function: this.string(null),
      description: this.string(null),
      query: this.string(null),
      author: this.string(null),
      created_at: this.string(null),

      //name have vbeen added to be able to reach out the specific rule from a dataset
      name: this.string(null),
      // relationships
      dataset: this.belongsTo(ObservationDataset, "dataset_id"),
      rule_metrics: this.hasOne(RulesMetric, "rule_id"),
    };
  }
}
