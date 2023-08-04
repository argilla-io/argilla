import { Dataset } from "./Dataset";
import { Field } from "./field/Field";
import { Question } from "./question/Question";

export class DatasetSetting {
  constructor(
    public readonly dataset: Dataset,
    public readonly questions: Question[] = [],
    public readonly fields: Field[] = []
  ) {}
}
