import { Model } from "@vuex-orm/core";
import { RecordField as RecordFieldModel } from "../record-field/RecordField.model";
import { RecordResponse as RecordResponseModel } from "../record-response/RecordResponse.model";
import { RECORD_STATUS } from "./record.queries";
class Record extends Model {
  static entity = "records";

  static fields() {
    return {
      id: this.uid(),
      dataset_id: this.attr(null),
      record_status: this.string(RECORD_STATUS.PENDING),
      record_index: this.number(0),

      // relationships
      record_responses: this.hasMany(RecordResponseModel, "record_id"),
      record_fields: this.hasMany(RecordFieldModel, "record_id"),
    };
  }

  static mutators() {
    return {
      record_status(value) {
        return value && value.toUpperCase();
      },
    };
  }
}

export { Record };
