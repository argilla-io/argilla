import { Filter, FilterWithOption, FilterWithScore } from "../common/Filter";
import { Question } from "../question/Question";

class ConfigurationValues extends FilterWithOption {
  constructor(
    public readonly question: Question,
    public operator: "and" | "or" = "and"
  ) {
    super(
      "values",
      question.settings.options.map(({ value }) => {
        return { selected: false, label: value.toString() };
      })
    );
  }

  get valueParams() {
    const params = JSON.stringify({
      values: super.valueParams,
      operator: this.operator,
    });

    return `${this.name}=${params}`;
  }

  completeMetadata(value: string) {
    try {
      const { values, operator } = JSON.parse(value);

      super.completeMetadata(values);

      this.operator = operator;
    } catch {
      // NOTHING
    }
  }
}

class ConfigurationScore extends FilterWithScore {
  constructor(public readonly min: number, public readonly max: number) {
    super("score", min, max);
  }

  get isInteger(): boolean {
    return true;
  }

  get settings() {
    return {
      min: this.min,
      max: this.max,
    };
  }

  get valueParams() {
    return `${this.name}=${super.valueParams}`;
  }
}

class ConfigurationAgent extends FilterWithOption {
  constructor(agents: string[]) {
    super(
      "agent",
      agents.map((value) => {
        return { selected: false, label: value };
      })
    );
  }

  get valueParams() {
    return `${this.name}=${super.valueParams}`;
  }
}

class SuggestionFilter extends Filter {
  public readonly configurations = [];

  constructor(private readonly question: Question) {
    super();

    this.configurations.push(new ConfigurationScore(10, 90));
    this.configurations.push(new ConfigurationValues(question));
    this.configurations.push(new ConfigurationAgent(["model", "human"]));
  }

  get name(): string {
    return this.question.name;
  }

  get isAnswered(): boolean {
    return this.configurations.some((c) => c.isAnswered);
  }

  get valueParams() {
    return this.configurations
      .filter((c) => c.isAnswered)
      .map((c) => c.valueParams)
      .join("|");
  }

  clear(): void {
    this.configurations.forEach((c) => c.clear());
  }

  completeMetadata(value: string) {
    const params = value.split("|");

    params.forEach((param) => {
      const [name, value] = param.split(/=(.*)/s);
      const configuration = this.configurations.find((c) => c.name === name);
      if (configuration) {
        configuration.completeMetadata(value);
      }
    });
  }
}

export class SuggestionFilterList {
  public readonly questions: SuggestionFilter[];
  private readonly filteredSuggestions: SuggestionFilter[] = [];
  private latestCommit: string[] = [];

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
    this.questions.forEach((m) => m.clear());

    if (!params.length) return;

    const suggestionFilter = params.map((metadata) => {
      const [name, value] = metadata.split(/:(.*)/s);
      return { name, value };
    });

    suggestionFilter.forEach(({ name, value }) => {
      const category = this.findByCategory(name);
      if (category) {
        category.completeMetadata(value);

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

  private convertToRouteParam(): string[] {
    return this.toQueryParams().map((metadata) => {
      return `${metadata.name}:${metadata.value}`;
    });
  }

  private toQueryParams() {
    return this.filteredSuggestions.map((m) => {
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
