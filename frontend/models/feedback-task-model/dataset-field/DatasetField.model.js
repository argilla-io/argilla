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
      component_type: this.string(null).nullable(),
      settings: this.attr(null),
    };
  }
}

export { DatasetField };
