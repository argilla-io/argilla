import { Model } from "@vuex-orm/core";

class Vector extends Model {
  static entity = "vectors";

  static fields() {
    return {
      id: this.uid(),
      vector_name: this.attr(null),
      values: this.attr([]),

      // relationship
      //TODO : link the vector Model to the record model
      dataset_id: this.attr(null),
      record_id: this.attr(null),
    };
  }
}

export { Vector };
