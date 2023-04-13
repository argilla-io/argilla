import { Model } from "@vuex-orm/core";
import { RecordField } from "../record-field/RecordField.model";
import { RecordResponse as RecordResponseModel } from "../record-response/RecordResponse.model";

class Record extends Model {
  static entity = "records";
  static primaryKey = ["record_id", "dataset_id"];

  static fields() {
    return {
      id: this.uid(),
      dataset_id: this.attr(null),

      // relationships
      record_responses: this.hasMany(RecordResponseModel, "record_id"),
      record_fields: this.hasMany(RecordField, "record_id"),
    };
  }
}

export { Record };
