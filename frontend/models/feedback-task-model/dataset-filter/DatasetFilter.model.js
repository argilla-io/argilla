import { Model } from "@vuex-orm/core";

class DatasetFilter extends Model {
  static entity = "datasetFilters";

  static fields() {
    return {
      id: this.uid(),
      name: this.attr(null),
      dataset_id: this.attr(null),
      value: this.attr(null),
      options: this.attr([]),
      placeholder: this.string(null).nullable(),
      component_type: this.string(null).nullable(),
    };
  }
}

export { DatasetFilter };
