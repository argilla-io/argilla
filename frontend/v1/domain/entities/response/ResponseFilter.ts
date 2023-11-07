import { Question } from "../question/Question";

class ResponseFilter {
  constructor(private readonly question: Question) {}

  get name() {
    return this.question.name;
  }

  get title() {
    return this.question.title;
  }
}

export class ResponseFilterList {
  public readonly questions: ResponseFilter[];

  constructor(questions: Question[]) {
    this.questions = questions
      .filter(this.visibleTypeOfQuestions)
      .map((question) => new ResponseFilter(question));
  }

  private visibleTypeOfQuestions(question: Question): boolean {
    return (
      question.isMultiLabelType ||
      question.isSingleLabelType ||
      question.isRatingType
    );
  }
}
