import { Criteria } from "../common/Criteria";
import { ResponseSearch } from "./ResponseFilter";

export class ResponseCriteria extends Criteria {
  public value: ResponseSearch[] = [];
  complete(urlParams: string) {
    if (!urlParams) return;

    urlParams.split("+").forEach((m) => {
      const [name, value] = m.split(/:(.*)/s);

      this.value.push({
        name,
        value: value.split(","),
      });
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

    return this.createParams().join("+");
  }

  get backendParams(): string[] {
    if (!this.isCompleted) return [];

    return this.createParams();
  }

  private createParams(): string[] {
    return this.value.map((m) => {
      return `${m.name}:${m.value.join(",")}`;
    });
  }
}
