import { Model } from "@vuex-orm/core";
import { TokenClassificationDataset } from "../TokenClassification";

class TokenGlobalEntity extends Model {
  static entity = "tokenGlobalEntities";
  static primaryKey = ["text", "color_id"];

  static fields() {
    return {
      id: this.uid(),
      color_id: this.attr(null),
      text: this.string(null),
      dataset_id: this.attr(null),
      is_activate: this.attr(false),
      // relationships
      dataset: this.belongsTo(TokenClassificationDataset, "dataset_id"),
    };
  }

  // get token_global_entity_id() {
  //   return `${this.text}.${this.color_id}`;
  // }
}

const formatDatasetIdForTokenGlobalEntityModel = (dataset_id) =>
  dataset_id.join(".");
export { TokenGlobalEntity, formatDatasetIdForTokenGlobalEntityModel };
