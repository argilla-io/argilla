import { Model } from "@vuex-orm/core";
import { DatasetQuestion } from "../dataset-question/DatasetQuestion.model";
import { Record } from "../record/Record.model";

class FeedbackDataset extends Model {
  static entity = "feedbackDatasets";

  static fields() {
    return {
      id: this.uid(),
      name: this.string(""),
      guidelines: this.string(""),
      workspace_id: this.attr(null),
      workspace_name: this.attr(null),
      inserted_at: this.attr(null),
      updated_at: this.attr(null),
      total_records: this.number(null).nullable(),

      // relationships
      dataset_questions: this.hasMany(DatasetQuestion, "dataset_id"),
      records: this.hasMany(Record, "dataset_id"),
    };
  }
}

export { FeedbackDataset };
