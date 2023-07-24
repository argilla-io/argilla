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

export class Question {
  private suggestion: Suggestion;
  public answer: QuestionAnswer;

  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly description: string,
    public readonly datasetId: string,
    public readonly title: string,
    public readonly isRequired: boolean,
    public readonly settings: any
  ) {
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

  clearAnswer() {
    this.answer.clear();
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
