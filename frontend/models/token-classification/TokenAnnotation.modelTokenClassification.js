import { Model } from "@vuex-orm/core";
import { TokenEntity } from "./TokenEntity.modelTokenClassification";
import { TokenRecord } from "./TokenRecord.modelTokenClassification";

class TokenAnnotation extends Model {
  static entity = "tokenAnnotations";
  static primaryKey = ["agent", "record_id"];

  static fields() {
    return {
      id: this.uid(),
      agent: this.string(null),
      entities: this.attr([]),
      record_id: this.attr(null),
      // name have been added to be able to reach out the specific annotation from a dataset primarykey
      query: this.string(null),

      // relationships
      token_records: this.belongsTo(TokenRecord, "record_id"),
      token_entities: this.morphMany(
        TokenEntity,
        "token_entitable_id",
        "token_entitable_type"
      ),
    };
  }
}

const getTokenAnnotationModelPrimaryKey = ({ agent, record_id }) => [
  agent,
  record_id,
];

export { TokenAnnotation, getTokenAnnotationModelPrimaryKey };
