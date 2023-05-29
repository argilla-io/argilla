import { Model } from "@vuex-orm/core";

class RecordResponse extends Model {
  static entity = "recordResponses";
  static primaryKey = ["id", "question_name"];

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
