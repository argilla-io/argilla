import {
  QuestionSetting,
  QuestionPrototype,
} from "../question/QuestionSetting";
import { QuestionType } from "../question/QuestionType";

export const availableQuestionTypes = [
  QuestionType.from("label_selection"),
  QuestionType.from("multi_label_selection"),
  QuestionType.from("ranking"),
  QuestionType.from("text"),
  QuestionType.from("span"),
  QuestionType.from("rating"),
];

export class QuestionCreation {
  public readonly settings: QuestionSetting;
  public title: string;

  constructor(
    public readonly name: string,
    public required: boolean,
    settings: QuestionPrototype
  ) {
    this.settings = new QuestionSetting(settings);
    this.title = this.name;
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
