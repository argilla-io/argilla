import { Model } from "@vuex-orm/core";
import { TokenClassificationDataset } from "../TokenClassification";
import { TokenAnnotation } from "./TokenAnnotation.modelTokenClassification";
import { TokenPrediction } from "./TokenPrediction.modelTokenClassification";

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

      // relationship
      dataset: this.belongsTo(TokenClassificationDataset, "dataset_id"),
      token_annotation: this.hasOne(TokenAnnotation, "record_id"),
      token_prediction: this.hasOne(TokenPrediction, "record_id"),
    };
  }
}

const formatAnnotationPredictionid = (prefix, datasetPrimaryKey) =>
  `${prefix}__${datasetPrimaryKey}`;

export { TokenRecord, formatAnnotationPredictionid };
