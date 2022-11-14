import { Model } from "@vuex-orm/core";
import { TokenClassificationDataset } from "../TokenClassification";
import { TokenAnnotation } from "./TokenAnnotation.modelTokenClassification";

class TokenRecord extends Model {
  static entity = "tokenRecords";

  static fields() {
    return {
      id: this.uid(),
      search_keywords: this.attr([]),
      status: this.string(""),
      tokens: this.attr([]),
      text: this.attr([]),
      dataset_id: this.attr(null),
      // annotation: this.attr({}), // FIXME need to be removed and used only annotationS
      prediction: this.attr({}),

      // relationship
      dataset: this.belongsTo(TokenClassificationDataset, "dataset_id"),
      token_annotation: this.hasOne(TokenAnnotation, "record_id"),
    };
  }

  get annotatedEntities() {
    const numberOfAnnotation = Object.keys(this.annotation).length;

    if (numberOfAnnotation) {
      return this.annotation.entities;
    }

    return [];
  }
}

export { TokenRecord };
