import { Criteria } from "../common/Criteria";
import { RangeValue } from "../common/Filter";
import { MetadataSearch } from "./MetadataFilter";

export class MetadataCriteria extends Criteria {
  public value: MetadataSearch[] = [];
  complete(urlParams: string) {
    if (!urlParams) return;

    urlParams.split("~").forEach((metadata) => {
      const [name] = metadata.split(".");

      const score = this.getRangeValue(metadata);

      if (score) {
        this.value.push({
          name,
          value: {
            ge: score.ge,
            le: score.le,
          },
        });
      } else {
        const values = metadata.split(".").slice(1);

        this.value.push({
          name,
          value: values,
        });
      }
    });
  }

  withValue(metadataCriteria: MetadataCriteria) {
    this.value = metadataCriteria.value.map((v) => {
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

        const values = response.value as string[];

        return `${response.name}.${values.map((v) => v).join(".")}`;
      })
      .join("~");
  }
}
