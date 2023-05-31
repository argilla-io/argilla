import { Model } from "@vuex-orm/core";

class DatasetField extends Model {
  static entity = "datasetFields";

  static fields() {
    return {
      id: this.uid(),
      name: this.attr(null),
      dataset_id: this.attr(null),
      order: this.number(0),
      title: this.string(""),
      is_required: this.boolean(false),
      use_markdown: this.boolean(true),
      component_type: this.string(null).nullable(),
    };
  }
}

export { DatasetField };
