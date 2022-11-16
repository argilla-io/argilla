import { Model } from "@vuex-orm/core";
import { TokenEntity } from "./TokenEntity.modelTokenClassification";
import { TokenRecord } from "./TokenRecord.modelTokenClassification";

class TokenPrediction extends Model {
  static entity = "predictions";

  static fields() {
    return {
      id: this.uid(),
      agent: this.string(null),
      entities: this.attr([]),
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
const formatEntityIdForPrediction = (id) => `${id}_PREDICTION`;
export { TokenPrediction, formatEntityIdForPrediction };
