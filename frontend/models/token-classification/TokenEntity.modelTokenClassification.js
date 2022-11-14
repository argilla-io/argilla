import { Model } from "@vuex-orm/core";
// import { TokenAnnotation } from "./TokenAnnotation.modelTokenClassification";

// import { TokenGlobalEntity } from "./TokenGlobalEntity.modelTokenClassification";

class TokenEntity extends Model {
  static entity = "tokenEntities";
  static primaryKey = ["label", "record_id", "start"]; // NOTE : carefull with the primary key unique for annotation & prediction

  static fields() {
    return {
      id: this.uid(),
      record_id: this.string(null),
      label: this.attr(null),
      start: this.attr(null),
      end: this.attr(null),
      score: this.attr(null),
      token_entitable_id: this.attr(null),
      token_entitable_type: this.attr(null),

      // relationship
      token_entitable: this.morphTo(
        "token_entitable_id",
        "token_entitable_type"
      ),

      //   token_global_entity_id: this.string(""),
      // relationships
      //   token_global_entity: this.hasOne(
      //     TokenGlobalEntity,
      //     "token_global_entity_id"
      //   ),
    };
  }
}
const getTokenEntitableIdPrimaryKey = ({ label, record_id, start, end }) =>
  `${label}.${record_id}.${start}.${end}`;

export { TokenEntity, getTokenEntitableIdPrimaryKey };
