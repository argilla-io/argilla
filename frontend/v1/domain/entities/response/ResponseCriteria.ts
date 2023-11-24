import { Criteria } from "../common/Criteria";
import { ResponseSearch } from "./ResponseFilter";

export class ResponseCriteria extends Criteria {
  public value: ResponseSearch[] = [];
  complete(urlParams: string) {
    if (!urlParams) return;

    this.value = JSON.parse(urlParams);
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

    return JSON.stringify(this.value);
  }
}
