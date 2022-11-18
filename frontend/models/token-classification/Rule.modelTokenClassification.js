import { Model } from "@vuex-orm/core";
import { ObservationDataset } from "../Dataset";
import RulesMetric from "./RulesMetric.modelTokenClassification";

class Rule extends Model {
  static entity = "rules";
  static primaryKey = ["query", "owner", "name"];

  static fields() {
    return {
      id: this.uid(),
      dataset_id: this.attr(null),
      label: this.attr(null),
      labeling_function: this.attr(null),
      description: this.string(null),
      query: this.string(null),
      author: this.string(null),
      created_at: this.string(null),
      is_saved_in_dataset: this.boolean(true),
      //name have been added to be able to reach out the specific rule from a dataset primarykey
      owner: this.string(null),
      name: this.string(null),
      // relationships
      dataset: this.belongsTo(ObservationDataset, "dataset_id"),
      rule_metrics: this.hasOne(RulesMetric, "rule_id"),
    };
  }
}

const getRuleModelPrimaryKey = ({ query, owner, name }) => [query, owner, name];

export { Rule, getRuleModelPrimaryKey };
