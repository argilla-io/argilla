import { Model } from "@vuex-orm/core";

class GlobalLabel extends Model {
  static entity = "globalLabels";
  static primaryKey = ["text", "dataset_id"];

  static fields() {
    return {
      id: this.uid(),
      order: this.number(null),
      color_id: this.attr(null),
      text: this.string(null),
      dataset_id: this.attr(null),
      is_activate: this.attr(false),
      shortcut: this.attr(null),
      is_saved_in_back: this.boolean(false),
    };
  }

  static mutators() {
    return {
      text(value) {
        return value.toUpperCase();
      },
    };
  }
}

const formatDatasetIdForGlobalLabelModel = (dataset_id) => dataset_id.join(".");

export { GlobalLabel, formatDatasetIdForGlobalLabelModel };
