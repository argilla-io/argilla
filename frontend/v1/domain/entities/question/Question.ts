import { Answer } from "../IAnswer";
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
    description: string,
    public readonly datasetId: string,
    title: string,
    public readonly isRequired: boolean,
    public settings: any
  ) {
    this.answer = this.createEmptyAnswers();
    this.description = description;
    this.title = title;

    this.initializeOriginal();
  }

  private _description: string;
  public get description(): string {
    return this._description;
  }

  public set description(newDescription: string) {
    this._description = newDescription?.trim() ?? "";
  }

  private _title: string;
  public get title(): string {
    return this._title;
  }

  public set title(newTitle: string) {
    this._title = newTitle?.trim() ?? "";
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
      this.title !== this.original.title ||
      this.description !== this.original.description ||
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

  public get isQuestionValid(): boolean {
    return (
      this.validate().title.length === 0 &&
      this.validate().description.length === 0
    );
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

  clone(questionReference: Question) {
    this.answer = questionReference.answer;
  }

  responseIfUnanswered(answer: Answer) {
    if (this.suggestion) {
      this.answer.responseIfUnanswered(this.suggestion);
    } else if (answer) {
      this.answer.responseIfUnanswered(answer);
    }
  }

  response(answer: Answer) {
    if (!answer) return;

    this.answer.response(answer);
  }

  addSuggestion(suggestion: Suggestion) {
    if (!suggestion) return;

    this.suggestion = suggestion;
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
