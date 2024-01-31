import { Criteria } from "../common/Criteria";
import { RangeValue, ValuesOption } from "../common/Filter";
import { ResponseSearch } from "./ResponseFilter";

export class ResponseCriteria extends Criteria {
  public value: ResponseSearch[] = [];

  complete(urlParams: string) {
    if (!urlParams) return;

    urlParams.split("~").forEach((response) => {
      const [name, ...rest] = response.split(".");

      const score = this.getRangeValue(response);

      if (score) {
        this.value.push({
          name,
          value: {
            ge: score.ge,
            le: score.le,
          },
        });

        return;
      }

      if (rest[0] === "operator" && rest[2] === "values") {
        const operator = rest[1];
        const values = rest.slice(3);

        this.value.push({
          name,
          value: {
            operator: operator as ValuesOption["operator"],
            values,
          },
        });

        return;
      }

      const values = response.split(".").slice(1);

      this.value.push({
        name,
        value: values,
      });
    });
  }

  withValue(responseCriteria: ResponseCriteria) {
    this.value = responseCriteria.value.map((v) => {
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
      .map((response) => {
        const rangeValue = response.value as RangeValue;

        if ("ge" in rangeValue && "le" in rangeValue) {
          return `${response.name}.ge${rangeValue.ge}.le${rangeValue.le}`;
        }

        const valuesOption = response.value as ValuesOption;

        if ("operator" in valuesOption && valuesOption) {
          return `${response.name}.operator.${
            valuesOption.operator
          }.values.${valuesOption.values.join(".")}`;
        }

        const values = response.value as string[];

        return `${response.name}.${values.join(".")}`;
      })
      .join("~");
  }

  get or() {
    if (!this.isCompleted) return [];

    const orResponses = this.value.filter((s) => {
      const { operator } = s.value as ValuesOption;

      return operator !== "and";
    });

    return orResponses.map((r) => {
      const { operator, values } = r.value as ValuesOption;

      if (operator) {
        return {
          name: r.name,
          value: values,
        };
      }

      return {
        name: r.name,
        value: r.value,
      };
    });
  }

  get and() {
    if (!this.isCompleted) return [];

    const andResponses = this.value.filter((s) => {
      const { operator } = s.value as ValuesOption;

      return operator === "and";
    });

    return andResponses.flatMap((s) => {
      const value = s.value as ValuesOption;

      return value.values.map((value) => {
        return {
          name: s.name,
          value,
        };
      });
    });
  }
}
