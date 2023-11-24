import { Criteria } from "../common/Criteria";
import { RangeValue } from "../common/Filter";

export type ValuesOption = {
  values: string[];
  operator?: "and" | "or";
};

export interface ConfigurationSearch {
  name: "score" | "value" | "agent";
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

    this.value = JSON.parse(urlParams) as SuggestionSearch[];
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

    return JSON.stringify(this.value);
  }

  get or() {
    if (!this.isCompleted) return [];

    const orSuggestions = this.value.filter((s) =>
      s.value.some((v) => {
        const { operator } = v.value as ValuesOption;

        return operator !== "and";
      })
    );

    return orSuggestions.flatMap((s) => {
      return s.value.map((v) => {
        return {
          question: { name: s.name },
          configuration: {
            name: v.name,
            value: v.value,
          },
        };
      });
    });
  }

  get and() {
    if (!this.isCompleted) return [];

    const andSuggestions = this.value.filter((s) =>
      s.value.some((v) => {
        const { operator } = v.value as ValuesOption;

        return operator === "and";
      })
    );

    return andSuggestions.flatMap((s) => {
      return s.value.flatMap((v) => {
        const value = v.value as ValuesOption;
        return value.values.map((m) => {
          return {
            question: { name: s.name },
            configuration: {
              name: v.name,
              value: m,
            },
          };
        });
      });
    });
  }
}
