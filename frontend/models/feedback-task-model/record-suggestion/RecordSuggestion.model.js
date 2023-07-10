import { Model } from "@vuex-orm/core";

class RecordSuggestion extends Model {
  static entity = "recordSuggestions";
  static primaryKey = ["id", "question_id"];

  static fields() {
    return {
      id: this.uid(),
      question_id: this.attr(null),
      question_name: this.attr(null),
      score: this.attr(null),
      agent: this.attr(null),
      type: this.attr(null),
      value: this.attr(null),
      record_id: this.attr(null),
    };
  }
}

export { RecordSuggestion };
