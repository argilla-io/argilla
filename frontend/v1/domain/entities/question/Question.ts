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
    this.answer = this.createEmptyAnswers();
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { options, ...rest } = settings;
    this.original = {
      title,
      description,
      settings: rest,
    };
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

  clearAnswer() {
    this.answer.clear();
  }

  public get isModified(): boolean {
    return (
      this.title?.trim() !== this.original.title ||
      this.description?.trim() !== this.original.description ||
      this.settings.use_markdown !== this.original.settings.use_markdown ||
      this.settings.visible_options !== this.original.settings.visible_options
    );
  }

  restore() {
    this.title = this.original.title;
    this.description = this.original.description;
    this.settings = {
      ...this.settings,
      ...this.original.settings,
    };
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
}
