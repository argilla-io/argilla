import { FilterWithOption } from "../common/Filter";
import { Question } from "../question/Question";

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
  private latestCommit: string[] = [];

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

    return this.hasChangesSinceLatestCommitWith(this.convertToRouteParam());
  }

  hasChangesSinceLatestCommitWith(compare: string[]) {
    return this.latestCommit.join("") !== compare.join("");
  }

  commit(): string[] {
    this.synchronizeFilteredMetadata();

    this.latestCommit = this.convertToRouteParam();

    return this.latestCommit;
  }

  initializeWith(params: string[]) {
    this.responses.forEach((m) => m.clear());

    if (!params.length) return;

    const responsesFilter = params.map((metadata) => {
      const [name, value] = metadata.split(/:(.*)/s);
      return { name, value };
    });

    responsesFilter.forEach(({ name, value }) => {
      const metadata = this.findByCategory(name);
      if (metadata) {
        metadata.completeMetadata(value);

        if (this.filteredResponses.includes(metadata)) return;

        this.filteredResponses.push(metadata);
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

  private convertToRouteParam(): string[] {
    return this.toQueryParams().map((metadata) => {
      return `${metadata.name}:${metadata.value}`;
    });
  }

  private toQueryParams() {
    return this.filteredResponses.map((m) => {
      return {
        name: m.name,
        value: m.valueParams,
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
