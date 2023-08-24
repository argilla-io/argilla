import { isEqual, cloneDeep } from "lodash";
import { Field } from "../field/Field";
import { Question } from "../question/Question";
import { Suggestion } from "../question/Suggestion";
import { RecordAnswer } from "./RecordAnswer";

const DEFAULT_STATUS = "pending";

export class Record {
  private originalQuestions: Question[];

  constructor(
    public readonly id: string,
    public readonly datasetId: string,
    public readonly questions: Question[],
    public readonly fields: Field[],
    public answer: RecordAnswer,
    private readonly suggestions: Suggestion[],
    public updatedAt: string,
    public readonly arrayOffset: number
  ) {
    this.completeQuestion();
  }

  get status() {
    return this.answer?.status ?? DEFAULT_STATUS;
  }

  get isSubmitted() {
    return this.status === "submitted";
  }

  get isDiscarded() {
    return this.status === "discarded";
  }

  get isSavedDraft() {
    return this.status === "draft";
  }

  get isModified() {
    return (
      this.originalQuestions && !isEqual(this.originalQuestions, this.questions)
    );
  }

  discard(answer: RecordAnswer) {
    this.originalQuestions = null;
    this.answer = answer;

    this.updatedAt = answer.updatedAt;

    this.restore();
  }

  submit(answer: RecordAnswer) {
    this.originalQuestions = null;
    this.answer = answer;

    this.updatedAt = answer.updatedAt;

    this.restore();
  }

  clear() {
    this.questions.forEach((question) => question.clearAnswer());

    this.answer = null;
  }

  restore() {
    this.completeQuestion();

    this.originalQuestions = cloneDeep(this.questions);
  }

  get hasAnyQuestionAnswered() {
    return this.questions.some((question) => question.answer.isValid);
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
      const answerForQuestion = this.answer?.value[question.name];

      if (answerForQuestion) {
        question.answerQuestionWithResponse(answerForQuestion);

        return question;
      }

      if (!this.answer) {
        const suggestion = this.suggestions?.find(
          (s) => s.questionId === question.id
        );

        if (suggestion) {
          question.answerQuestionWithSuggestion(suggestion);
        }
      }

      return question;
    });
  }
}
