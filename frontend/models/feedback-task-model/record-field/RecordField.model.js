import { Model } from "@vuex-orm/core";
import { Record } from "../record/Record.model";
import { FieldRecord as FieldRecordPivot } from "../pivot-table/FieldRecord.pivot";

class RecordField extends Model {
  static entity = "recordFields";

  static fields() {
    return {
      id: this.uid(),
      title: this.string(null).nullable(),
      text: this.string(null).nullable(),

      // relationships
      records: this.belongsToMany(
        Record,
        FieldRecordPivot,
        "record_field_id",
        "record_id"
      ),
    };
  }
}

export { RecordField };
