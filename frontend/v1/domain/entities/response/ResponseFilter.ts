import {
  Filter,
  FilterWithOption,
  FilterWithScore,
  OptionForFilter,
  RangeValue,
  ValuesOption,
} from "../common/Filter";
import { Question } from "../question/Question";

export interface ResponseSearch {
  name: string;
  value: string[] | RangeValue | ValuesOption;
}

class FilterWithOptionAndOperator {
  public operator: "and" | "or" = "and";
  public readonly options: FilterWithOption;

  constructor(private readonly question: Question) {
    this.options = new FilterWithOption(
      question.name,
      question.settings.options.map(({ value, text }) => {
        return {
          selected: false,
          value: value.toString(),
          text,
        } as OptionForFilter;
      })
    );
  }

  get value(): string[] | ValuesOption {
    if (this.question.isMultiLabelType)
      return {
        operator: this.operator,
        values: this.options.value,
      };

    return this.options.value;
  }

  filterByText(text: string) {
    return this.options.filterByText(text);
  }

  get selectedOptions(): OptionForFilter[] {
    return this.options.selectedOptions;
  }

  complete(value: string[] | ValuesOption) {
    if ("operator" in value) {
      this.operator = value.operator;
      this.options.complete(value.values);
    } else {
      this.options.complete(value as string[]);
    }
  }

  clear() {
    this.options.clear();
  }

  get hasOperator() {
    return this.question.isMultiLabelType;
  }

  get isAnswered(): boolean {
    return this.options.isAnswered;
  }
}

class ResponseFilter extends Filter {
  public readonly rangeValue: FilterWithScore;
  public readonly options: FilterWithOptionAndOperator;
  constructor(private readonly question: Question) {
    super();

    if (this.isTerms) {
      this.options = new FilterWithOptionAndOperator(question);
    } else {
      this.rangeValue = new FilterWithScore(
        question.name,
        question.settings.options[0].value,
        question.settings.options[question.settings.options.length - 1].value,
        true
      );
    }
  }

  get tooltip() {
    return this.question.title;
  }

  get isTerms() {
    return !this.question.isRatingType;
  }

  get name(): string {
    return this.question.name;
  }

  get value(): string[] | RangeValue | ValuesOption {
    if (this.isTerms) {
      return this.options.value;
    }

    return this.rangeValue.value;
  }

  complete(value: string[] | RangeValue | ValuesOption): void {
    if (this.isTerms) {
      this.options.complete(value as string[] | ValuesOption);
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
    this.synchronizeFiltered();

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

  private synchronizeFiltered() {
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
