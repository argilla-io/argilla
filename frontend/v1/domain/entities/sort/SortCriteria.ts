import { Criteria } from "../common/Criteria";
import { SortSearch } from "./SortList";

export class SortCriteria extends Criteria {
  public value: SortSearch[] = [];

  complete(urlParams: string) {
    if (!urlParams) return;

    urlParams.split("~").forEach((sort) => {
      const value = this.parseUrlParams(sort);

      this.value.push(value);
    });
  }

  witValue(value: SortSearch[]) {
    this.value = value.map((v) => ({ ...v }));
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
      .map((sort) => {
        if (sort.property) {
          return `${sort.entity}.${sort.name}.${sort.property}.${sort.order}`;
        }

        return `${sort.entity}.${sort.name}.${sort.order}`;
      })
      .join("~");
  }

  private parseUrlParams(sort: string): SortSearch {
    const [entity, name, third, fourth] = sort.split(".");

    if (third && fourth) {
      return {
        entity,
        name,
        order: fourth,
        property: third,
      } as SortSearch;
    }

    return {
      entity,
      name,
      order: third,
    } as SortSearch;
  }
}
