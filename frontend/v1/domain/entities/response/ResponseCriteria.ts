import { Criteria } from "../common/Criteria";
import { RangeValue } from "../common/Filter";
import { ResponseSearch } from "./ResponseFilter";

export class ResponseCriteria extends Criteria {
  public value: ResponseSearch[] = [];

  complete(urlParams: string) {
    if (!urlParams) return;

    urlParams.split("+").forEach((metadata) => {
      const [name, value] = metadata.split(".");

      if (value.includes("~")) {
        const values = value.split("~");

        this.value.push({
          name,
          value: values,
        });
      } else {
        const [ge, le] = value.split("le.");

        this.value.push({
          name,
          value: {
            ge: Number(ge),
            le: Number(le),
          },
        });
      }
    });
  }

  withValue(value: ResponseSearch[]) {
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

    return this.value
      .map((response) => {
        const rangeValue = response.value as RangeValue;

        if ("ge" in rangeValue && "le" in rangeValue) {
          return `${response.name}.ge.${rangeValue.ge}le.${rangeValue.le}`;
        }

        const values = response.value as string[];

        return `${response.name}.${values.map((v) => v).join("~")}`;
      })
      .join("+");
  }
}
