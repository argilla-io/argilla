import { Model } from "@vuex-orm/core";
import { TokenEntity } from "./TokenEntity.modelTokenClassification";
import { TokenRecord } from "./TokenRecord.modelTokenClassification";

class TokenAnnotation extends Model {
  static entity = "annotations";

  static fields() {
    return {
      id: this.uid(),
      agent: this.string(null),
      record_id: this.attr(null),

      // relationships
      token_record: this.belongsTo(TokenRecord, "record_id"),
      token_entities: this.morphMany(
        TokenEntity,
        "entitable_id",
        "entitable_type"
      ),
    };
  }
}

const formatEntityIdForAnnotation = (prefix) => `${prefix}__ANNOTATION`;

export { TokenAnnotation, formatEntityIdForAnnotation };
