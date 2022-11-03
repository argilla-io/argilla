import { Model } from "@vuex-orm/core";
import { TokenClassificationDataset } from "../TokenClassification";

class TokenEntity extends Model {
  static entity = "tokenEntities";
  static primaryKey = ["text", "color_id"];

  static fields() {
    return {
      id: this.uid(),
      color_id: this.attr(null),
      text: this.string(null),
      dataset_id: this.attr(null),
      is_activate: this.attr(false),
      // // relationships
      dataset: this.belongsTo(TokenClassificationDataset, "dataset_id"),
    };
  }
}

const formatDatasetIdForTokenEntityModel = (dataset_id) => dataset_id.join(".");
export { TokenEntity, formatDatasetIdForTokenEntityModel };
