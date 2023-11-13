import { FilterWithOption } from "../common/Filter";
import { Question } from "../question/Question";

export interface ResponseSearch {
  name: string;
  value: string[];
}

class ResponseFilter extends FilterWithOption {
  constructor(question: Question) {
    super(
      question.name,
      question.settings.options.map(({ value }) => {
        return { selected: false, label: value.toString() };
      })
    );
  }
}

export class ResponseFilterList {
  public readonly responses: ResponseFilter[];
  private readonly filteredResponses: ResponseFilter[] = [];
  private latestCommit: ResponseSearch[] = [];

  constructor(questions: Question[]) {
    this.responses = questions
      .filter(this.visibleTypeOfQuestions)
      .map((question) => new ResponseFilter(question));
  }

  get filteredCategories() {
    return this.filteredResponses;
  }

  get filtered() {
    return this.responses.filter((m) => m.isAnswered);
  }

  get hasChangesSinceLatestCommit() {
    if (this.filteredResponses.length !== this.filtered.length) return true;

    if (this.filtered.some((f) => !this.filteredResponses.includes(f)))
      return true;

    return this.hasChangesSinceLatestCommitWith(this.createCommit());
  }

  hasChangesSinceLatestCommitWith(compare: ResponseSearch[]) {
    return JSON.stringify(this.latestCommit) !== JSON.stringify(compare);
  }

  commit(): ResponseSearch[] {
    this.synchronizeFilteredMetadata();

    this.latestCommit = this.createCommit();

    return this.latestCommit;
  }

  complete(params: ResponseSearch[]) {
    if (!this.hasChangesSinceLatestCommitWith(params)) return;

    this.responses.forEach((m) => m.clear());

    if (!params.length) return;

    params.forEach(({ name, value }) => {
      const response = this.findByCategory(name);
      if (response) {
        response.complete(value);

        if (this.filteredResponses.includes(response)) return;

        this.filteredResponses.push(response);
      }
    });

    this.commit();
  }

  private findByCategory(category: string) {
    return this.responses.find((cat) => cat.name === category);
  }

  private synchronizeFilteredMetadata() {
    const newFiltered = this.filtered.filter(
      (category) => !this.filteredResponses.includes(category)
    );
    newFiltered.forEach((f) => {
      this.filteredResponses.push(f);
    });

    const removedFilters = this.filteredResponses.filter(
      (category) => !this.filtered.includes(category)
    );
    removedFilters.forEach((f) => {
      const indexOf = this.filteredResponses.indexOf(f);

      this.filteredResponses.splice(indexOf, 1);
    });
  }

  private createCommit(): ResponseSearch[] {
    return this.filteredResponses.map((m) => {
      return {
        name: m.name,
        value: m.value,
      };
    });
  }

  private visibleTypeOfQuestions(question: Question): boolean {
    return (
      question.isMultiLabelType ||
      question.isSingleLabelType ||
      question.isRatingType
    );
  }
}
