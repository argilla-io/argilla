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

  // ACCESSORS
  get total_record_with_params() {
    return { value: this.total_record, color: "blue" };
  }
  get responses_count_with_params() {
    return { value: this.responses_count, color: "grey" };
  }
  get responses_submitted_with_params() {
    return { value: this.responses_submitted, color: "red" };
  }
  get responses_discarded_with_params() {
    return { value: this.responses_discarded, color: "yellow" };
  }
}

export { DatasetMetric };
