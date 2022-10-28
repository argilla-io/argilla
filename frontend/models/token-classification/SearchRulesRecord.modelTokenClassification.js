import { Model } from "@vuex-orm/core";
import { Rule } from "./Rule.modelTokenClassification";

class SearchRulesRecord extends Model {
  static entity = "searchRulesRecords";

  static fields() {
    return {
      id: this.string(null),
      rule_id: this.string(null),
      status: this.string(null),
      annotation: this.attr({}),
      annotations: this.attr({}),
      prediction: this.attr({}),
      predictions: this.attr({}),
      search_keywords: this.attr([]),
      last_updated: this.string(null),
      text: this.attr(""),
      tokens: this.attr([]),

      // relationships
      rule: this.belongsTo(Rule, "rule_id"),
    };
  }
}

export { SearchRulesRecord };
