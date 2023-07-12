import { Field } from "./Field";
import { Question } from "./Question";

export class Feedback {
  constructor(
    public readonly questions: Question[] = [],
    public readonly fields: Field[] = []
  ) {}

  public records: any[] = [];

  addRecords(records: unknown[]) {
    this.records = [...this.records, ...records];
  }

  updateResponse(response: any) {
    const record = this.records.find((r) => r.id === response.record_id);

    record.responses = record.responses.map((r) => {
      if (r.id === response.id) return response;

      return r;
    });
  }

  addResponse(response: any) {
    const record = this.records.find((r) => r.id === response.record_id);

    record.responses.push(response);
  }

  clearRecord(recordId: string, status: string) {
    const record = this.records.find((r) => r.id === recordId);

    if (!record) return;

    record.responses = [];
    record.status = status;
  }

  getAnswer(recordId: string, userId: string) {
    return this.questionsWithRecordAnswers(recordId, userId);
  }

  getAnswerWithNoSuggestions() {
    this.questions.forEach((question) => {
      question.clearAnswer();
    });

    return this.questions;
  }

  questionsWithRecordAnswers(recordId: string, userId: string) {
    const record = this.records.find((r) => r.id === recordId);

    const response = record?.responses.filter(
      (response) => response.user_id === userId
    )[0];

    return this.questions.map((question) => {
      const userAnswer = response?.values[question.name];
      if (userAnswer) {
        question.answerQuestionWithResponse(userAnswer);
      } else {
        const suggestion = record.suggestions?.find(
          (s) => s.question_id === question.id
        );

        question.answerQuestionWithSuggestion(suggestion);
      }

      return question;
    });
  }
}
