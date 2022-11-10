import { Model } from "@vuex-orm/core";
import { TokenRecord } from "./TokenRecord.modelTokenClassification";

class TokenAnnotation extends Model {
  static entity = "tokenAnnotations";
  static primaryKey = ["agent", "record_id", "owner", "name"];

  static fields() {
    return {
      id: this.uid(),
      agent: this.string(null),
      entities: this.attr([]),
      record_id: this.attr(null),
      //name have been added to be able to reach out the specific annotation from a dataset primarykey
      query: this.string(null),
      owner: this.string(null),
      name: this.string(null),

      // relationships
      token_records: this.belongsTo(TokenRecord, "record_id"),
    };
  }
}

const getTokenAnnotationModelPrimaryKey = ({
  agent,
  record_id,
  owner,
  name,
}) => [agent, record_id, owner, name];

export { TokenAnnotation, getTokenAnnotationModelPrimaryKey };
