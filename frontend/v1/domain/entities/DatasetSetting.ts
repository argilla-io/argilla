import { Dataset } from "./Dataset";
import { Field } from "./field/Field";
import { Question } from "./question/Question";
import { Vector } from "./vector/Vector";

export class DatasetSetting {
  constructor(
    public readonly dataset: Dataset,
    public readonly questions: Question[] = [],
    public readonly fields: Field[] = [],
    public readonly vectors: Vector[] = []
  ) {}
}
