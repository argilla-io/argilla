import { Model } from "@vuex-orm/core";
import { RecordField } from "../record-field/RecordField.model";
import { FieldRecord as FieldRecordPivot } from "../pivot-table/FieldRecord.pivot";

class Record extends Model {
  static entity = "records";
  static primaryKey = ["record_id", "dataset_id"];

  static fields() {
    return {
      id: this.uid(),
      dataset_id: this.attr(null),

      // relationships
      record_fields: this.belongsToMany(
        RecordField,
        FieldRecordPivot,
        "record_id",
        "record_field_id"
      ),
    };
  }
}

export { Record };
