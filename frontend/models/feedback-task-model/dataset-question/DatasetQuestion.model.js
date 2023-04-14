import { Model } from "@vuex-orm/core";

class DatasetQuestion extends Model {
  static entity = "datasetQuestions";
  static primaryKey = ["component_type", "question"];

  static fields() {
    return {
      id: this.uid(),
      dataset_id: this.attr(null),
      order: this.number(0),
      question: this.string(""),
      outputs: this.attr([]),
      placeholder: this.string(null).nullable(),
      is_required: this.boolean(false),
      component_type: this.string(null).nullable(),
      tooltip_message: this.string(null).nullable(),
    };
  }
}

export { DatasetQuestion };
