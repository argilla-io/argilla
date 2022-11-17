import { Model } from "@vuex-orm/core";
import { TokenClassificationDataset } from "../TokenClassification";
import { TokenAnnotation } from "./TokenAnnotation.modelTokenClassification";
import { TokenPrediction } from "./TokenPrediction.modelTokenClassification";
import { TokenRuleAnnotation } from "./TokenRuleAnnotation.modelTokenClassification";

class TokenRecord extends Model {
  static entity = "records";

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
      token_rule_annotations: this.hasOne(TokenRuleAnnotation, "record_id"),
    };
  }
}

const formatAnnotationPredictionid = (prefix, datasetPrimaryKey) =>
  `${prefix}__${datasetPrimaryKey}`;

export { TokenRecord, formatAnnotationPredictionid };
