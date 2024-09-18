import { isEqual, cloneDeep } from "lodash";
import { Field } from "../field/Field";
import { Question } from "../question/Question";
import { Suggestion } from "../question/Suggestion";
import { Score } from "../similarity/Score";
import { MetadataRecord } from "../metadata/MetadataRecord";
import { TaskDistribution } from "../distribution/TaskDistribution";
import { RecordAnswer } from "./RecordAnswer";

const DEFAULT_STATUS = "pending";

export class Record {
  // eslint-disable-next-line no-use-before-define
  private original: Record;
  public readonly score: Score;
  public readonly taskDistribution: TaskDistribution;
  constructor(
    public readonly id: string,
    public readonly datasetId: string,
    public readonly questions: Question[],
    public readonly fields: Field[],
    public answer: RecordAnswer,
    private readonly suggestions: Suggestion[],
    score: number,
    public readonly page: number,
    public readonly metadata: MetadataRecord,
    distributionStatus: "completed" | "pending",
    public readonly insertedAt: Date,
    public readonly updatedAt?: Date
  ) {
    this.completeQuestion();
    this.score = new Score(score);
    this.taskDistribution = new TaskDistribution(distributionStatus);
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

    this.initialize();
  }

  submit(answer: RecordAnswer) {
    this.answer = answer;

    this.initialize();
  }

  clear() {
    this.questions.forEach((question) => question.clearAnswer());

    this.answer = null;

    this.initialize();
  }

  answerWith(recordReference: Record) {
    this.questions
      .filter((q) => !q.isSpanType)
      .forEach((question) => {
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

      if (this.isPending) {
        question.response(suggestion);
      } else {
        question.response(answer);
      }

      return question;
    });
  }
}
