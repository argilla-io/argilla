import { Model } from "@vuex-orm/core";

class RecordResponse extends Model {
  static entity = "recordResponses";
  static primaryKey = ["question_name", "record_id", "user_id"];

  static fields() {
    return {
      id: this.uid(),
      options: this.attr([]),
      question_name: this.attr(null),
      record_id: this.attr(null),
      user_id: this.attr(null),
    };
  }
}

export { RecordResponse };
