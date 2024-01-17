import { isEqual, cloneDeep } from "lodash";
import { Field } from "../field/Field";
import { Question } from "../question/Question";
import { Suggestion } from "../question/Suggestion";
import { Score } from "../similarity/Score";
import { RecordAnswer } from "./RecordAnswer";

const DEFAULT_STATUS = "pending";

export class Record {
  // eslint-disable-next-line no-use-before-define
  private original: Record;
  public updatedAt?: string;
  public readonly score: Score;
  constructor(
    public readonly id: string,
    public readonly datasetId: string,
    public readonly questions: Question[],
    public readonly fields: Field[],
    public answer: RecordAnswer,
    private readonly suggestions: Suggestion[],
    score: number,
    public readonly page: number
  ) {
    this.completeQuestion();
    this.updatedAt = answer?.updatedAt;
    this.score = new Score(score);
  }

  get status() {
    return this.answer?.status ?? DEFAULT_STATUS;
  }

  get isPending() {
    return this.status === DEFAULT_STATUS;
  }

  get isSubmitted() {
    return this.status === "submitted";
  }

  get isDiscarded() {
    return this.status === "discarded";
  }

  get isDraft() {
    return this.status === "draft";
  }

  get isModified() {
    const { original, ...rest } = this;

    return !!original && !isEqual(original, rest);
  }

  discard(answer: RecordAnswer) {
    this.answer = answer;
    this.updatedAt = answer.updatedAt;

    this.initialize();
  }

  submit(answer: RecordAnswer) {
    this.answer = answer;
    this.updatedAt = answer.updatedAt;

    this.initialize();
  }

  clear() {
    this.questions.forEach((question) => question.clearAnswer());

    this.answer = null;

    this.initialize();
  }

  answerWith(recordReference: Record) {
    this.questions.forEach((question) => {
      const questionReference = recordReference.questions.find(
        (q) => q.id === question.id
      );

      if (!questionReference) return;

      question.clone(questionReference);
    });
  }

  initialize() {
    this.completeQuestion();

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { original, ...rest } = this;

    this.original = cloneDeep(rest);
  }

  get hasAnyQuestionAnswered() {
    return this.questions.some(
      (question) => question.answer.isValid || question.answer.isPartiallyValid
    );
  }

  questionAreCompletedCorrectly() {
    const requiredQuestionsAreCompletedCorrectly = this.questions
      .filter((input) => input.isRequired)
      .every((input) => {
        return input.isAnswered;
      });

    const optionalQuestionsCompletedAreCorrectlyEntered = this.questions
      .filter((input) => !input.isRequired)
      .every((input) => {
        return input.hasValidValues;
      });

    return (
      requiredQuestionsAreCompletedCorrectly &&
      optionalQuestionsCompletedAreCorrectlyEntered
    );
  }

  private completeQuestion() {
    return this.questions.map((question) => {
      const answer = this.answer?.value[question.name];
      const suggestion = this.suggestions?.find(
        (s) => s.questionId === question.id
      );
      question.addSuggestion(suggestion);
      if (this.isPending || this.isDraft) {
        question.responseIfUnanswered(answer);
      } else {
        question.response(answer);
      }

      return question;
    });
  }
}
