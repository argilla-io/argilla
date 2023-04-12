import { Model } from "@vuex-orm/core";

class FieldRecord extends Model {
  static entity = "field_record";

  static fields() {
    return {
      id: this.uid(),
      record_id: this.attr(null),
      record_field_id: this.attr(null),
    };
  }
}

export { FieldRecord };
