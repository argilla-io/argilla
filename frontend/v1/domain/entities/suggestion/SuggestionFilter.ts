import { Question } from "../question/Question";

interface IConfiguration {
  id: string;
}

class ConfigurationValues implements IConfiguration {
  constructor(public readonly question: Question) {}
  get id(): string {
    return "values";
  }

  get conditionals(): string[] {
    return ["and", "or"];
  }
}

class ConfigurationScore implements IConfiguration {
  constructor(public readonly min: number, public readonly max: number) {}

  get id(): string {
    return "score";
  }
}

class ConfigurationAgent implements IConfiguration {
  constructor(public readonly agents: string[]) {}

  get id(): string {
    return "agent";
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
