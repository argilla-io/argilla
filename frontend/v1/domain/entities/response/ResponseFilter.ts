import {
  Filter,
  FilterWithOption,
  FilterWithScore,
  RangeValue,
} from "../common/Filter";
import { Question } from "../question/Question";

export interface ResponseSearch {
  name: string;
  value: string[] | RangeValue;
}

class ResponseFilter extends Filter {
  public readonly rangeValue: FilterWithScore;
  public readonly options: FilterWithOption;
  constructor(private readonly question: Question) {
    super();

    if (this.isTerms) {
      this.options = new FilterWithOption(
        question.name,
        question.settings.options.map(({ value }) => {
          return { selected: false, label: value.toString() };
        })
      );
    } else {
      this.rangeValue = new FilterWithScore(
        question.name,
        question.settings.options[0].value,
        question.settings.options[question.settings.options.length - 1].value,
        true
      );
    }
  }

  get isTerms() {
    return !this.question.isRatingType;
  }

  get name(): string {
    return this.question.name;
  }

  get value(): unknown {
    if (this.isTerms) {
      return this.options.value;
    }

    return this.rangeValue.value;
  }

  complete(value: unknown): void {
    if (this.isTerms) {
      this.options.complete(value as string[]);
    } else {
      this.rangeValue.complete(value as RangeValue);
    }
  }

  clear(): void {
    if (this.isTerms) {
      this.options.clear();
    } else {
      this.rangeValue.clear();
    }
  }

  get isAnswered(): boolean {
    if (this.isTerms) return this.options.isAnswered;

    return this.rangeValue.isAnswered;
  }
}

export class ResponseFilterList {
  public readonly responses: ResponseFilter[];
  private readonly filteredResponses: ResponseFilter[] = [];
  private latestCommit: ResponseSearch[] = [];

  constructor(questions: Question[]) {
    this.responses = questions.map((question) => new ResponseFilter(question));
  }

  get hasFilters() {
    return this.responses.length > 0;
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
}
