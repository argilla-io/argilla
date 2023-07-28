import { Field } from "../Field";
import { Question } from "../question/Question";
import { Suggestion } from "../question/Suggestion";
import { RecordAnswer } from "./RecordAnswer";

const DEFAULT_STATUS = "pending";

export class Record {
  constructor(
    public readonly id: string,
    public readonly datasetId: string,
    public readonly questions: Question[],
    public readonly fields: Field[],
    public answer: RecordAnswer,
    private readonly suggestions: Suggestion[],
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

  discard(answer: RecordAnswer) {
    this.answer = answer;
  }

  submit(answer: RecordAnswer) {
    this.answer = answer;
  }

  clear() {
    this.questions.forEach((question) => question.clearAnswer());

    this.answer = null;
  }

  restore() {
    this.completeQuestion();
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
