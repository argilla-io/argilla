import { Color } from "../color/Color";
import { Guard } from "../error";
import {
  MultiLabelQuestionAnswer,
  QuestionAnswer,
  RankingQuestionAnswer,
  RatingLabelQuestionAnswer,
  SingleLabelQuestionAnswer,
  SpanQuestionAnswer,
  TextQuestionAnswer,
} from "../question/QuestionAnswer";
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
  public settings: QuestionSetting;
  public title: string;
  public readonly id: string;
  constructor(
    public readonly name: string,
    public required: boolean,
    public column: string,
    settings: QuestionPrototype
  ) {
    this.settings = new QuestionSetting(settings);
    this.title = this.name;
    this.id = this.name;
    this.column = column;

    this.initialize();
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

  get isTextType(): boolean {
    return this.type.isTextType;
  }

  get isSpanType(): boolean {
    return this.type.isSpanType;
  }

  get isRatingType(): boolean {
    return this.type.isRatingType;
  }

  get isMultiLabelType(): boolean {
    return this.type.isMultiLabelType;
  }

  get isSingleLabelType(): boolean {
    return this.type.isSingleLabelType;
  }

  get isRankingType(): boolean {
    return this.type.isRankingType;
  }

  get answer(): QuestionAnswer {
    return this.createInitialAnswers();
  }

  public setSettings(settings: QuestionPrototype) {
    this.settings = new QuestionSetting(settings);
    this.initialize();
  }

  private initialize() {
    if (this.isSpanType) {
      this.settings.options = this.settings.options.map((option) => {
        return {
          ...option,
          color: option.color
            ? Color.from(option.color)
            : Color.generate(option.value),
        };
      });
    }

    this.markAsRequired();
  }

  private createInitialAnswers(): QuestionAnswer {
    if (this.isTextType) {
      return new TextQuestionAnswer(this.type, "");
    }

    if (this.isSpanType) {
      return new SpanQuestionAnswer(
        this.type,
        this.name,
        this.settings.options
      );
    }

    if (this.isRatingType) {
      return new RatingLabelQuestionAnswer(
        this.type,
        this.name,
        this.settings.options
      );
    }

    if (this.isMultiLabelType) {
      return new MultiLabelQuestionAnswer(
        this.type,
        this.name,
        this.settings.options
      );
    }

    if (this.isSingleLabelType) {
      return new SingleLabelQuestionAnswer(
        this.type,
        this.name,
        this.settings.options
      );
    }

    if (this.isRankingType) {
      return new RankingQuestionAnswer(
        this.type,
        this.name,
        this.settings.options
      );
    }

    Guard.throw(
      `Question answer for type ${this.type} is not implemented yet.`
    );
  }
}
