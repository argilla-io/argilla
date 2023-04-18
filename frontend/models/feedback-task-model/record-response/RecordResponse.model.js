import { Model } from "@vuex-orm/core";

class RecordResponse extends Model {
  static entity = "recordResponses";
  static primaryKey = ["question_id", "record_id"];

  static fields() {
    return {
      id: this.uid(),
      options: this.attr([]),
      question_id: this.attr(null),
      record_id: this.attr(null),
      user_id: this.attr(null),
    };
  }
}

export { RecordResponse };
