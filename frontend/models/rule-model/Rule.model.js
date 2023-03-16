import { Model } from "@vuex-orm/core";
// import { ObservationDataset } from "../Dataset";
// import RulesMetric from "./RulesMetric.modelTokenClassification";

class Rule extends Model {
  static entity = "rules";
  static primaryKey = ["query", "dataset_workspace", "dataset_name"];

  static fields() {
    return {
      query: this.attr(null),
      dataset_id: this.attr(null),
      dataset_workspace: this.attr(null),
      dataset_name: this.attr(null),
      description: this.attr(""),
      author: this.attr(null),
      created_at: this.attr(null),
      labels: this.attr([]),
      labelling_function: this.attr(null), // this is only for token classification
      is_saved_in_dataset: this.boolean(true),

      // relationships
      // dataset: this.belongsTo(ObservationDataset, "dataset_id"),
      // rule_metrics: this.hasOne(RulesMetric, "rule_id"),
    };
  }
}

const getRuleModelPrimaryKey = ({ query, owner, name }) => [query, owner, name];

export { Rule, getRuleModelPrimaryKey };
