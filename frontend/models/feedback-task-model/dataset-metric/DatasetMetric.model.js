import { Model } from "@vuex-orm/core";

class DatasetMetric extends Model {
  static entity = "datasetMetrics";
  static primaryKey = ["user_id", "dataset_id"];

  static fields() {
    return {
      user_id: this.attr(null),
      dataset_id: this.attr(null),
      total_record: this.number(0),
      responses_count: this.number(0),
      responses_submitted: this.number(0),
      responses_discarded: this.number(0),
    };
  }
}

export { DatasetMetric };
