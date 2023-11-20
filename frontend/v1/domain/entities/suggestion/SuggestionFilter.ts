import {
  Filter,
  FilterWithOption,
  FilterWithScore,
  OptionForFilter,
} from "../common/Filter";
import { Question } from "../question/Question";
import { Agent } from "./Agent";
import { ConfigurationSearch, SuggestionSearch } from "./SuggestionCriteria";

class ConfigurationValues extends Filter {
  private readonly options: FilterWithOption;

  constructor(
    public readonly question: Question,
    public operator: "and" | "or" = "and"
  ) {
    super();

    this.options = new FilterWithOption(
      "values",
      question.settings.options.map(({ value }) => {
        return { selected: false, label: value.toString() };
      })
    );
  }

  filterByText(text: string) {
    return this.options.filterByText(text);
  }

  get selectedOptions(): OptionForFilter[] {
    return this.options.selectedOptions;
  }

  get name(): string {
    return this.options.name;
  }

  get isAnswered(): boolean {
    return this.options.isAnswered;
  }

  complete(value: { values: string[]; operator?: "and" | "or" }) {
    const { values, operator } = value;

    this.options.complete(values);

    this.operator = operator;
  }

  get hasOperator() {
    return this.question.isMultiLabelType;
  }

  get value(): {
    values: string[];
    operator?: "and" | "or";
  } {
    if (this.hasOperator)
      return {
        values: this.options.value,
        operator: this.operator,
      };

    return {
      values: this.options.value,
    };
  }

  clear(): void {
    this.options.clear();
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
        return { selected: false, label: value };
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

    this.configurations.push(new ConfigurationScore(0, 1));
    this.configurations.push(new ConfigurationValues(question));
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
          name: c.name as "score" | "values" | "agent",
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
    this.questions = questions
      .filter(this.visibleTypeOfQuestions)
      .map((question) => new SuggestionFilter(question));
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
  }

  hasChangesSinceLatestCommitWith(compare: SuggestionSearch[]) {
    return JSON.stringify(this.latestCommit) !== JSON.stringify(compare);
  }

  commit(): SuggestionSearch[] {
    this.synchronizeFilteredMetadata();

    this.latestCommit = this.createCommit();

    return this.latestCommit;
  }

  complete(params: SuggestionSearch[]) {
    if (!this.hasChangesSinceLatestCommitWith(params)) return;

    this.questions.forEach((m) => m.clear());

    if (!params.length) return;

    params.forEach(({ name, value }) => {
      const category = this.findByCategory(name);
      if (category) {
        category.complete(value);

        if (this.filteredSuggestions.includes(category)) return;

        this.filteredSuggestions.push(category);
      }
    });

    this.commit();
  }

  private findByCategory(category: string) {
    return this.questions.find((cat) => cat.name === category);
  }

  private synchronizeFilteredMetadata() {
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

  private visibleTypeOfQuestions(question: Question): boolean {
    return (
      question.isMultiLabelType ||
      question.isSingleLabelType ||
      question.isRatingType
    );
  }
}
