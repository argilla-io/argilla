import { Criteria } from "../common/Criteria";
import { MetadataSearch } from "./MetadataFilter";

export class MetadataCriteria extends Criteria {
  public value: MetadataSearch[] = [];
  complete(urlParams: string) {
    if (!urlParams) return;

    this.value = JSON.parse(urlParams) as MetadataSearch[];
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

    return JSON.stringify(this.value);
  }
}
