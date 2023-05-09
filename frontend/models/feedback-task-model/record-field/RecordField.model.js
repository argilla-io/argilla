import { Model } from "@vuex-orm/core";

class RecordField extends Model {
  static entity = "recordFields";

  static fields() {
    return {
      id: this.uid(),
      field_name: this.string(null).nullable(),
      text: this.string(null).nullable(),
      record_id: this.attr(null),
    };
  }
}

export { RecordField };
