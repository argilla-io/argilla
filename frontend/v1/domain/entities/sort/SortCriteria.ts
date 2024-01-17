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

  withValue(sortCriteria: SortCriteria) {
    this.value = sortCriteria.value.map((v) => ({ ...v }));
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
      .map(({ property, entity, name, order }) => {
        if (property) {
          return `${entity}.${name}.${property}.${order}`;
        }

        return `${entity}.${name}.${order}`;
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
