import { Model } from "@vuex-orm/core";
import { DatasetQuestion } from "../dataset-question/DatasetQuestion.model";
import { DatasetField } from "../dataset-field/DatasetField.model";
import { DatasetMetric } from "../dataset-metric/DatasetMetric.model";
import { DatasetFilter } from "../dataset-filter/DatasetFilter.model";
import { Record } from "../record/Record.model";

class FeedbackDataset extends Model {
  static entity = "feedbackDatasets";

  static fields() {
    return {
      id: this.uid(),
      name: this.string(""),
      task: this.string("FeedbackTask"),
      guidelines: this.string(null).nullable(),
      workspace_id: this.attr(null),
      workspace_name: this.attr(null),
      inserted_at: this.attr(null),
      updated_at: this.attr(null),

      // relationships
      dataset_questions: this.hasMany(DatasetQuestion, "dataset_id"),
      dataset_fields: this.hasMany(DatasetField, "dataset_id"),
      dataset_metrics: this.hasMany(DatasetMetric, "dataset_id"),
      dataset_filters: this.hasMany(DatasetFilter, "dataset_id"),
      records: this.hasMany(Record, "dataset_id"),
    };
  }
}

export { FeedbackDataset };
