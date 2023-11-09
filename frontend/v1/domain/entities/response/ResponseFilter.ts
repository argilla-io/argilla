import { FilterWithOption } from "../common/Filter";
import { Question } from "../question/Question";

class ResponseFilter extends FilterWithOption {
  constructor(question: Question) {
    super(
      question.name,
      question.title,
      question.settings.options.map(({ value }) => {
        return { selected: false, label: value.toString() };
      })
    );
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
