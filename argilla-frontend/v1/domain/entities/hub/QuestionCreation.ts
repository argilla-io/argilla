import {
  QuestionSetting,
  QuestionPrototype,
} from "../question/QuestionSetting";
import { QuestionType } from "../question/QuestionType";

export class QuestionCreation {
  public readonly settings: QuestionSetting;

  constructor(
    public readonly name: string,
    public required: boolean,
    settings: QuestionPrototype
  ) {
    this.settings = new QuestionSetting(settings);
  }

  get title() {
    return this.name;
  }

  get type() {
    return this.settings.type;
  }

  set type(value: QuestionType) {
    this.settings.type = value;
  }

  get options() {
    return this.settings.options;
  }

  markAsRequired() {
    this.required = true;
  }
}
