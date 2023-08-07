import { RecordAnswer } from "../record/RecordAnswer";
import {
  QuestionAnswer,
  QuestionType,
  TextQuestionAnswer,
  SingleLabelQuestionAnswer,
  RatingLabelQuestionAnswer,
  MultiLabelQuestionAnswer,
  RankingQuestionAnswer,
} from "./QuestionAnswer";
import { Suggestion } from "./Suggestion";

interface OriginalQuestion {
  title: string;
  description: string;
  settings: any;
}

export class Question {
  public answer: QuestionAnswer;
  private suggestion: Suggestion;
  private original: OriginalQuestion;

  constructor(
    public readonly id: string,
    public readonly name: string,
    public description: string,
    public readonly datasetId: string,
    public title: string,
    public readonly isRequired: boolean,
    public settings: any
  ) {
    this.initializeOriginal();

    this.answer = this.createEmptyAnswers();
  }

  public get isAnswered(): boolean {
    return this.answer.isValid;
  }

  public get hasValidValues(): boolean {
    return this.answer.hasValidValues;
  }

  public get type(): QuestionType {
    return this.settings.type.toLowerCase();
  }

  public get isRankingType(): boolean {
    return this.type === "ranking";
  }

  public get isMultiLabelType(): boolean {
    return this.type === "multi_label_selection";
  }

  public get isSingleLabelType(): boolean {
    return this.type === "label_selection";
  }

  public get isTextType(): boolean {
    return this.type === "text";
  }

  public get isRatingType(): boolean {
    return this.type === "rating";
  }

  public get matchSuggestion(): boolean {
    return !!this.suggestion && this.answer.matchSuggestion(this.suggestion);
  }

  public get isModified(): boolean {
    return (
      this.title?.trim() !== this.original.title ||
      this.description?.trim() !== this.original.description ||
      this.settings.use_markdown !== this.original.settings.use_markdown ||
      this.settings.visible_options !== this.original.settings.visible_options
    );
  }

  private MAX_DESCRIPTION_LENGTH = 500;
  private MAX_TITLE_LENGTH = 200;
  public validate(): Record<"title" | "description", string[]> {
    const validations: Record<"title" | "description", string[]> = {
      title: [],
      description: [],
    };

    if (!this.title) validations.title.push("This field is required.");

    if (this.title.length > this.MAX_TITLE_LENGTH)
      validations.title.push(
        `This must be less than ${this.MAX_TITLE_LENGTH}.`
      );

    if (this.description.length > this.MAX_DESCRIPTION_LENGTH)
      validations.description.push(
        `This must be less than ${this.MAX_DESCRIPTION_LENGTH}.`
      );

    return validations;
  }

  public get isTitleValid(): boolean {
    return this.validate().title.length === 0;
  }

  public get isDescriptionValid(): boolean {
    return this.validate().description.length === 0;
  }

  public get isQuestionValid(): boolean {
    return this.isTitleValid && this.isDescriptionValid;
  }

  clearAnswer() {
    this.answer.clear();
  }

  restore() {
    this.title = this.original.title;
    this.description = this.original.description;
    this.settings = {
      ...this.settings,
      ...this.original.settings,
    };
  }

  update() {
    this.initializeOriginal();
  }

  answerQuestionWithResponse(answer: RecordAnswer) {
    this.answer.complete(answer);
  }

  answerQuestionWithSuggestion(suggestion: Suggestion) {
    this.suggestion = suggestion;
    this.answer.complete(suggestion);
  }

  private createEmptyAnswers(): QuestionAnswer {
    if (this.isTextType) {
      return new TextQuestionAnswer(this.type, "");
    }

    if (this.isSingleLabelType) {
      return new SingleLabelQuestionAnswer(
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

    if (this.isRankingType) {
      return new RankingQuestionAnswer(
        this.type,
        this.name,
        this.settings.options
      );
    }
  }

  private initializeOriginal() {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { options, ...rest } = this.settings;
    this.original = {
      title: this.title,
      description: this.description,
      settings: rest,
    };
  }
}
