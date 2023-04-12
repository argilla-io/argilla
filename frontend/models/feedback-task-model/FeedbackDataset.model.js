import { Model } from "@vuex-orm/core";

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
    };
  }
}

export { FeedbackDataset };
