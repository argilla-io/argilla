import { OptionForFilter } from "../metadata/MetadataFilter";
import { Question } from "../question/Question";

interface IConfiguration {
  name: string;
}

class ConfigurationValues implements IConfiguration {
  public options: OptionForFilter[] = [];

  constructor(
    public readonly question: Question,
    public operator: "and" | "or" = "and"
  ) {
    this.options =
      this.question.settings.options?.map((value) => {
        return { selected: false, label: value.value.toString() };
      }) ?? [];
  }

  get name(): string {
    return "values";
  }

  public filterByText(text: string) {
    return this.options.filter((option) =>
      option.label.toLowerCase().includes(text.toLowerCase())
    );
  }

  public get selectedOptions(): OptionForFilter[] {
    return this.options.filter((option) => option.selected);
  }
}

class ConfigurationScore implements IConfiguration {
  public readonly value: any;
  constructor(public readonly min: number, public readonly max: number) {
    this.value = {
      ge: min,
      le: max,
    };
  }

  get name(): string {
    return "score";
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

class ConfigurationAgent implements IConfiguration {
  public options: OptionForFilter[] = [];

  constructor(public readonly agents: string[]) {
    this.options =
      this.agents.map((value) => {
        return { selected: false, label: value };
      }) ?? [];
  }

  get name(): string {
    return "agent";
  }

  public filterByText(text: string) {
    return this.options.filter((option) =>
      option.label.toLowerCase().includes(text.toLowerCase())
    );
  }

  public get selectedOptions(): OptionForFilter[] {
    return this.options.filter((option) => option.selected);
  }
}

class SuggestionFilter {
  public readonly configurations = [];
  constructor(private readonly question: Question) {
    this.configurations.push(new ConfigurationScore(10, 90));
    this.configurations.push(new ConfigurationValues(question));
    this.configurations.push(new ConfigurationAgent(["Test", "Test2"]));
  }

  get name() {
    return this.question.name;
  }

  get title() {
    return this.question.title;
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
