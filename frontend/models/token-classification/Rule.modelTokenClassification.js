import { Model } from "@vuex-orm/core";
import { ObservationDataset } from "../Dataset";
import RulesMetric from "./RulesMetric.modelTokenClassification";
import SearchRulesRecord from "./SearchRulesRecord.modelTokenClassification";

class Rule extends Model {
  static entity = "rules";
  static primaryKey = ["query", "owner", "name"];

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

      //name have been added to be able to reach out the specific rule from a dataset primarykey
      owner: this.string(null),
      name: this.string(null),
      // relationships
      dataset: this.belongsTo(ObservationDataset, "dataset_id"),
      rule_metrics: this.hasOne(RulesMetric, "rule_id"),
      search_rules_records: this.hasMany(SearchRulesRecord, "rule_id"),
    };
  }
}

const getRuleModelPrimaryKey = ({ query, owner, name }) => [query, owner, name];

export { Rule, getRuleModelPrimaryKey };
