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
}

export class SuggestionFilterList {
  public readonly questions: SuggestionFilter[];

  constructor(questions: Question[]) {
    this.questions = questions
      .filter(this.visibleTypeOfQuestions)
      .map((question) => new SuggestionFilter(question));
  }

  private visibleTypeOfQuestions(question: Question): boolean {
    return (
      question.isMultiLabelType ||
      question.isSingleLabelType ||
      question.isRatingType
    );
  }
}
