import { Criteria } from "../common/Criteria";
import { RangeValue, ValuesOption } from "../common/Filter";

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

    urlParams.split("~").forEach((suggestion) => {
      const [questionName, configurationName, ...rest] = suggestion.split(
        "."
      ) as [string, ConfigurationSearch["name"], ...string[]];

      if (configurationName === "score" || configurationName === "value") {
        const score = this.getRangeValue(suggestion);

        if (score) {
          const configuration = {
            name: configurationName,
            value: {
              ge: score.ge,
              le: score.le,
            },
          };

          return this.addConfiguration(questionName, configuration);
        }
      }

      if (configurationName === "value") {
        const operator = rest[0] === "operator" ? rest[1] : undefined;
        const values = operator ? rest.slice(3) : rest.slice(1);

        const configuration: ConfigurationSearch = {
          name: configurationName,
          value: {
            values,
          },
        };

        if (operator) {
          configuration.value = {
            ...configuration.value,
            operator: operator as ValuesOption["operator"],
          };
        }

        return this.addConfiguration(questionName, configuration);
      }

      if (configurationName === "agent") {
        const configuration = {
          name: configurationName,
          value: rest,
        };

        return this.addConfiguration(questionName, configuration);
      }
    });
  }

  withValue(suggestionCriteria: SuggestionCriteria) {
    this.value = suggestionCriteria.value.map((v) => {
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

    return this.value
      .flatMap((suggestion) => {
        return suggestion.value.map((v) => {
          const rangeValue = v.value as RangeValue;

          if ("ge" in rangeValue && "le" in rangeValue) {
            return `${suggestion.name}.${v.name}.ge${rangeValue.ge}.le${rangeValue.le}`;
          }

          const valuesOption = v.value as ValuesOption;

          if ("operator" in valuesOption && valuesOption) {
            return `${suggestion.name}.${v.name}.operator.${
              valuesOption.operator
            }.values.${valuesOption.values.join(".")}`;
          }

          // eslint-disable-next-line no-prototype-builtins
          if (valuesOption.hasOwnProperty("values") && valuesOption.values) {
            return `${suggestion.name}.${
              v.name
            }.values.${valuesOption.values.join(".")}`;
          }

          const values = v.value as string[];

          return `${suggestion.name}.${v.name}.${values.join(".")}`;
        });
      })
      .join("~");
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
      return s.value
        .filter((v) => v.name === "value")
        .flatMap((v) => {
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

  private addConfiguration(
    questionName: string,
    configuration: ConfigurationSearch
  ) {
    const question = this.value.find((v) => v.name === questionName);

    if (question) {
      question.value.push(configuration);

      return;
    }

    this.value.push({
      name: questionName,
      value: [configuration],
    });
  }
}
