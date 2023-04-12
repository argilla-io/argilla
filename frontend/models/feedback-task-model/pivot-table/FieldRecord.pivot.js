import { Model } from "@vuex-orm/core";

class FieldRecord extends Model {
  static entity = "field_record";
  static primaryKey = ["record_field_id", "record_id"];

  static fields() {
    return {
      id: this.uid(),
      record_id: this.attr(null),
      record_field_id: this.attr(null),
    };
  }
}

export { FieldRecord };
