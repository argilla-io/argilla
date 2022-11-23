import { Model } from "@vuex-orm/core";
import { TokenEntity } from "./TokenEntity.modelTokenClassification";
// import { TokenRecord } from "./TokenRecord.modelTokenClassification";

class TokenRuleAnnotation extends Model {
  static entity = "ruleAnnotations";

  static fields() {
    return {
      id: this.uid(),
      query_search: this.string(null),
      record_id: this.attr(null),

      // relationships
      // token_record: this.belongsTo(TokenRecord, "record_id"),
      token_entities: this.morphMany(
        TokenEntity,
        "entitable_id",
        "entitable_type"
      ),
    };
  }
}

const formatEntityIdForRuleAnnotation = (prefix) =>
  `${prefix}__RULE_ANNOTATION`;

export { TokenRuleAnnotation, formatEntityIdForRuleAnnotation };
