import { Criteria } from "../common/Criteria";
import { MetadataSearch } from "./MetadataFilter";

export class MetadataCriteria extends Criteria {
  public value: MetadataSearch[] = [];
  complete(urlParams: string) {
    if (!urlParams) return;

    urlParams
      .split("+")
      .map((metadata) => {
        const [name, value] = metadata.split(/:(.*)/s);
        return { name, value };
      })
      .forEach(({ name, value }) => {
        try {
          this.value.push({
            name,
            value: JSON.parse(value),
          });
        } catch (e) {
          // TODO: Manipulated
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

    return this.createParams().join("+");
  }

  get backendParams(): string[] {
    if (!this.isCompleted) return [];

    return this.createParams();
  }

  private createParams(): string[] {
    return this.value.map((m) => {
      return `${m.name}:${JSON.stringify(m.value)}`;
    });
  }
}
