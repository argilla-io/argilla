import { Criteria } from "../common/Criteria";
import { RangeValue } from "../common/Filter";
import { MetadataSearch } from "./MetadataFilter";

export class MetadataCriteria extends Criteria {
  public value: MetadataSearch[] = [];
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

  withValue(value: MetadataSearch[]) {
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
      .map((metadata) => {
        const rangeValue = metadata.value as RangeValue;

        if ("ge" in rangeValue && "le" in rangeValue) {
          return `${metadata.name}.ge.${rangeValue.ge}le.${rangeValue.le}`;
        }

        const values = metadata.value as string[];

        return `${metadata.name}.${values.map((v) => v).join("~")}`;
      })
      .join("+");
  }
}
