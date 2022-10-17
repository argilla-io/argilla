import { Model } from "@vuex-orm/core";
import Rule from "./Rule.modelTokenClassification";

export default class RulesMetric extends Model {
  static entity = "rulesMetrics";

  static fields() {
    return {
      id: this.uid(),
      coverage: this.number(null),
      coverage_annotated: this.number(null),
      total_records: this.number(null),
      annotated_records: this.number(null),
      rule_id: this.string(null),
      // relationships
      rule: this.belongsTo(Rule, "rule_id"),
    };
  }
}
