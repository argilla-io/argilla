import { Question } from "./Question";

class QuestionFilter {
  constructor(private readonly question: Question) {}

  get name() {
    return this.question.name;
  }

  get title() {
    return this.question.title;
  }
}

export class QuestionFilterList {
  public readonly questions: QuestionFilter[];

  constructor(questions: Question[]) {
    this.questions = questions.map((question) => new QuestionFilter(question));
  }
}
