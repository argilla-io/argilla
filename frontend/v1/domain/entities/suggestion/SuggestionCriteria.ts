import { Criteria } from "../common/Criteria";
import { RangeValue } from "../common/Filter";

type ValuesOption = {
  values: string[];
  operator?: "and" | "or";
};

export interface ConfigurationSearch {
  name: "score" | "values" | "agent";
  value: string[] | RangeValue | ValuesOption;
}

export interface SuggestionSearch {
  name: string;
  value: ConfigurationSearch[];
}

export class SuggestionCriteria extends Criteria {
  public value: SuggestionSearch[] = [];
  complete(urlParams: string) {
    if (!urlParams) return;

    try {
      urlParams.split("+").forEach((m) => {
        const [name, value] = m.split(/:(.*)/s);

        this.value.push({
          name,
          value: JSON.parse(value),
        });
      });
    } catch (error) {
      // TODO: Manipulated
    }
  }

  withValue(value: SuggestionSearch[]) {
    this.value = value.map((v) => {
      return {
        name: v.name,
        value: v.value,
      };
    });
  }

  reset() {
    this.value = [];
  }

  get isCompleted(): boolean {
    return this.value.length > 0;
  }

  get urlParams(): string {
    if (!this.isCompleted) return "";

    return this.createParams().join("+");
  }

  get or() {
    if (!this.isCompleted) return [];

    const orSuggestion = this.value.map((s) => {
      return s.value.map((v) => {
        return {
          question: { name: s.name },
          isRange: v.name === "score",
          configuration: {
            name: v.name,
            value: v.value,
          },
        };
      });
    });

    return orSuggestion.flatMap((s) => s);
  }

  get and() {
    if (!this.isCompleted) return [];

    const andSuggestions = this.value.map((s) => {
      return s.value
        .filter((v) => {
          const { operator } = v.value as ValuesOption;
          return operator === "and";
        })
        .map((v) => {
          return {
            question: { name: s.name },
            configuration: {
              name: v.name,
              value: v.value as string[],
            },
          };
        });
    });

    return andSuggestions.flatMap((s) => s);
  }

  private createParams(): string[] {
    return this.value.map((m) => {
      return `${m.name}:${JSON.stringify(m.value)}`;
    });
  }
}
