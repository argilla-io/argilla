import { Field } from "../field/Field";
import { Metadata } from "../metadata/Metadata";
import { Question } from "../question/Question";
import { Vector } from "../vector/Vector";
import { Dataset } from "./Dataset";

export class DatasetSetting {
  constructor(
    public readonly dataset: Dataset,
    public readonly questions: Question[] = [],
    public readonly fields: Field[] = [],
    public readonly vectors: Vector[] = [],
    public readonly metadataProperties: Metadata[] = []
  ) {}

  get hasVectors() {
    return this.vectors.length > 0;
  }

  get hasMetadataProperties() {
    return this.metadataProperties.length > 0;
  }

  get isModified(): boolean {
    return (
      this.isDatasetModified ||
      this.isQuestionsModified ||
      this.isFieldsModified ||
      this.isVectorsModified ||
      this.isMetadataPropertiesModified
    );
  }

  get isMetadataPropertiesModified(): boolean {
    return this.metadataProperties.some((m) => m.isModified);
  }

  get isVectorsModified(): boolean {
    return this.vectors.some((v) => v.isModified);
  }

  get isFieldsModified(): boolean {
    return this.fields.some((f) => f.isModified);
  }

  get isQuestionsModified(): boolean {
    return this.questions.some((q) => q.isModified);
  }

  get isDatasetModified(): boolean {
    return this.dataset?.isModified;
  }
}
