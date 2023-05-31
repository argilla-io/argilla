import { Model } from "@vuex-orm/core";

class DatasetQuestion extends Model {
  static entity = "datasetQuestions";

  static fields() {
    return {
      id: this.uid(),
      name: this.attr(null),
      dataset_id: this.attr(null),
      order: this.number(0),
      question: this.string(""),
      options: this.attr([]),
      placeholder: this.string(null).nullable(),
      is_required: this.boolean(false),
      use_markdown: this.boolean(true), //TODO - remove true (only for testing)
      component_type: this.string(null).nullable(),
      description: this.string(null).nullable(),
    };
  }
}

export { DatasetQuestion };
