import { FilterWithOption } from "../common/Filter";
import { Question } from "../question/Question";

class ResponseFilter extends FilterWithOption {
  constructor(private readonly question: Question) {
    super(
      question.name,
      question.settings.options.map(({ value }) => {
        return { selected: false, label: value.toString() };
      })
    );
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
