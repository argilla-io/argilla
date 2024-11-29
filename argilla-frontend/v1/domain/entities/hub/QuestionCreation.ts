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
import { Subset } from "./Subset";

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
  public required: boolean;
  public readonly originalColumn: string;
  constructor(
    private readonly subset: Subset,
    public readonly name: string,
    settings: QuestionPrototype,
    public column: string = "no mapping"
  ) {
    this.settings = new QuestionSetting(settings);
    this.title = this.name;
    this.id = this.name;

    this.originalColumn = column;

    this.initialize();
  }

  get wasAutoMapped(): boolean {
    return this.originalColumn !== "no mapping";
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

  get isRequired(): boolean {
    return this.required;
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

  get isValid(): boolean {
    const validation = this.validate();

    return validation.field.length === 0 && validation.options.length === 0;
  }

  validate(): Record<"options" | "field", string[]> {
    const validation = {
      options: [],
      field: [],
    };

    if (this.isSpanType) {
      if (
        !this.subset.textFields.some(
          (field) => field.name === this.settings.field
        ) ||
        !this.settings.field
      ) {
        validation.field.push("datasetCreation.questions.span.fieldRelated");
      }
    }

    if (this.isMultiLabelType || this.isSingleLabelType || this.isSpanType) {
      if (this.options.length < 2) {
        validation.options.push(
          "datasetCreation.questions.labelSelection.atLeastTwoOptions"
        );
      }

      if (this.options.some((option) => !option.id)) {
        validation.options.push(
          "datasetCreation.questions.labelSelection.optionsWithoutLabel"
        );
      }
    }

    if (this.isRatingType) {
      if (this.options.length < 2) {
        validation.options.push(
          "datasetCreation.questions.rating.atLeastTwoOptions"
        );
      }
    }

    return validation;
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
