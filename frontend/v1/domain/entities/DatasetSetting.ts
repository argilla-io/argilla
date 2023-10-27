import { Dataset } from "./Dataset";
import { Field } from "./field/Field";
import { Metadata } from "./metadata/Metadata";
import { Question } from "./question/Question";
import { Vector } from "./vector/Vector";

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
}
