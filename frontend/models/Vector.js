import { Model } from "@vuex-orm/core";

class Vector extends Model {
  static entity = "vectors";
  static primaryKey = ["vector_name", "dataset_id", "record_id"];

  static fields() {
    return {
      id: this.uid(),
      vector_name: this.attr(null),
      vector_values: this.attr([]),
      is_active: this.boolean(false),

      // relationship
      //TODO : link the vector Model to the record model
      dataset_id: this.attr(null),
      record_id: this.attr(null),
    };
  }
}

const getVectorModelPrimaryKey = ({ vector_name, dataset_id, record_id }) => [
  vector_name,
  dataset_id,
  record_id,
];

export { Vector, getVectorModelPrimaryKey };
