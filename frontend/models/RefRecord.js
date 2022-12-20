import { Model } from "@vuex-orm/core";

class RefRecord extends Model {
  static entity = "refRecords";
  static primaryKey = ["record_id", "dataset_id"];

  static fields() {
    return {
      id: this.uid(),
      dataset_id: this.attr(""),
      record_id: this.attr(""),
    };
  }
}

export { RefRecord };
