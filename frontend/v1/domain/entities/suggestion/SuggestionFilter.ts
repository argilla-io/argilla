import {
  Filter,
  FilterWithOption,
  FilterWithScore,
  OptionForFilter,
  RangeValue,
  ValuesOption,
} from "../common/Filter";
import { Question } from "../question/Question";
import { Agent } from "./Agent";
import { ConfigurationSearch, SuggestionSearch } from "./SuggestionCriteria";

class ConfigurationValues extends Filter {
  public readonly rangeValue: FilterWithScore;
  private readonly options: FilterWithOption;
  public operator: "and" | "or" = "and";

  constructor(public readonly question: Question) {
    super();

    if (this.isTerms) {
      this.options = new FilterWithOption(
        this.name,
        question.settings.options.map(({ value, text }) => {
          return {
            selected: false,
            value: value.toString(),
            text,
          } as OptionForFilter;
        })
      );
    } else {
      this.rangeValue = new FilterWithScore(
        this.name,
        this.question.settings.options[0].value,
        this.question.settings.options[
          this.question.settings.options.length - 1
        ].value,
        true
      );
    }
  }

  filterByText(text: string) {
    return this.options.filterByText(text);
  }

  get selectedOptions(): OptionForFilter[] {
    return this.options.selectedOptions;
  }

  get isAnswered(): boolean {
    if (this.isTerms) return this.options.isAnswered;

    return this.rangeValue.isAnswered;
  }

  get name() {
    return "value";
  }

  get isTerms() {
    return !this.question.isRatingType;
  }

  complete(value: { values: string[] | RangeValue; operator?: "and" | "or" }) {
    if (this.isTerms) {
      const { values, operator } = value;

      this.options.complete(values as string[]);

      this.operator = operator;
    } else {
      this.rangeValue.complete(value as RangeValue);
    }
  }

  get hasOperator() {
    return this.question.isMultiLabelType;
  }

  get value(): ValuesOption | RangeValue {
    if (this.isTerms) {
      if (this.hasOperator)
        return {
          values: this.options.value,
          operator: this.operator,
        };

      return {
        values: this.options.value,
      };
    }

    return this.rangeValue.value;
  }

  clear(): void {
    if (this.isTerms) return this.options.clear();

    this.rangeValue.clear();
  }
}

class ConfigurationScore extends FilterWithScore {
  constructor(public readonly min: number, public readonly max: number) {
    super("score", min, max);
  }
}

class ConfigurationAgent extends FilterWithOption {
  constructor(private readonly agents: string[] = []) {
    super(
      "agent",
      agents.map((value) => {
        return { selected: false, value };
      })
    );
  }

  get canFilter(): boolean {
    return this.agents.length > 0;
  }
}

class SuggestionFilter extends Filter {
  public readonly configurations: Filter[] = [];

  constructor(private readonly question: Question) {
    super();

    this.configurations.push(new ConfigurationValues(question));
    this.configurations.push(new ConfigurationScore(0, 1));
  }

  get tooltip(): string {
    return this.question.title;
  }

  get name(): string {
    return this.question.name;
  }

  get isAnswered(): boolean {
    return this.configurations.some((c) => c.isAnswered);
  }

  get value(): ConfigurationSearch[] {
    return this.configurations
      .filter((c) => c.isAnswered)
      .map((c) => {
        return {
          name: c.name as ConfigurationSearch["name"],
          value: c.value,
        };
      });
  }

  clear(): void {
    this.configurations.forEach((c) => c.clear());
  }

  addAgents(agents: string[]) {
    this.configurations.push(new ConfigurationAgent(agents));
  }

  complete(value: ConfigurationSearch[]) {
    value.forEach(({ name, value }) => {
      const configuration = this.configurations.find((c) => c.name === name);

      if (configuration) {
        configuration.complete(value);
      }
    });
  }
}

export class SuggestionFilterList {
  public readonly questions: SuggestionFilter[];
  private readonly filteredSuggestions: SuggestionFilter[] = [];
  private latestCommit: SuggestionSearch[] = [];

  constructor(questions: Question[]) {
    this.questions = questions.map(
      (question) => new SuggestionFilter(question)
    );
  }

  get hasFilters() {
    return this.questions.length > 0;
  }

  get filteredCategories() {
    return this.filteredSuggestions;
  }

  get filtered() {
    return this.questions.filter((m) => m.isAnswered);
  }

  get hasChangesSinceLatestCommit() {
    if (this.filteredSuggestions.length !== this.filtered.length) return true;

    if (this.filtered.some((f) => !this.filteredSuggestions.includes(f)))
      return true;

    return this.hasChangesSinceLatestCommitWith(this.createCommit());
  }

  addAgents(agents: Agent[] = []) {
    this.questions.forEach((q) => {
      q.addAgents(agents.find((a) => a.question.name === q.name)?.agents);
    });

    this.onComplete(this.latestCommit);
  }

  hasChangesSinceLatestCommitWith(compare: SuggestionSearch[]) {
    return JSON.stringify(this.latestCommit) !== JSON.stringify(compare);
  }

  commit(): SuggestionSearch[] {
    this.synchronizeFiltered();

    this.latestCommit = this.createCommit();

    return this.latestCommit;
  }

  complete(params: SuggestionSearch[]) {
    if (!this.hasChangesSinceLatestCommitWith(params)) return;

    this.questions.forEach((m) => m.clear());

    if (!params.length) return;

    this.onComplete(params);

    this.latestCommit = params;
  }

  private onComplete(params: SuggestionSearch[]) {
    params.forEach(({ name, value }) => {
      const category = this.findByCategory(name);
      if (category) {
        category.complete(value);

        if (this.filteredSuggestions.includes(category)) return;

        this.filteredSuggestions.push(category);
      }
    });
  }

  private findByCategory(category: string) {
    return this.questions.find((cat) => cat.name === category);
  }

  private synchronizeFiltered() {
    const newFiltered = this.filtered.filter(
      (category) => !this.filteredSuggestions.includes(category)
    );
    newFiltered.forEach((f) => {
      this.filteredSuggestions.push(f);
    });

    const removedFilters = this.filteredSuggestions.filter(
      (category) => !this.filtered.includes(category)
    );
    removedFilters.forEach((f) => {
      const indexOf = this.filteredSuggestions.indexOf(f);

      this.filteredSuggestions.splice(indexOf, 1);
    });
  }

  private createCommit(): SuggestionSearch[] {
    return this.filteredSuggestions.map((m) => {
      return {
        name: m.name,
        value: m.value,
      };
    });
  }
}
