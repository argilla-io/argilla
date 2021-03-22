import { Model } from "@vuex-orm/core";
import DatasetViewSettings from "./DatasetViewSettings";

const USER_DATA_METADATA_KEY = "rubrix.recogn.ai/ui/custom/userData.v1";

class ObservationDataset extends Model {
  static entity = "datasets";

  static primaryKey = "name";

  static fields() {
    return {
      name: this.string(null),
      metadata: this.attr(null),
      tags: this.attr(null),
      task: this.string(null),
      created_at: this.string(null),
      last_updated: this.string(null),
      viewSettings: this.hasOne(DatasetViewSettings, "id"),
    };
  }

  get visibleRecords() {
    return this.results.records.slice(
      0,
      this.viewSettings.pagination.size * this.viewSettings.pagination.page
    );
  }
}

export { ObservationDataset, USER_DATA_METADATA_KEY };
