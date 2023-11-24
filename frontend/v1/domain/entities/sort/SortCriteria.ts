import { Criteria } from "../common/Criteria";
import { SortSearch } from "./SortList";

export class SortCriteria extends Criteria {
  public value: SortSearch[] = [];

  complete(urlParams: string) {
    if (!urlParams) return;

    urlParams.split("+").forEach((sort) => {
      const [entity, name, property, order] = sort.split(".");
      const value = {
        entity,
        name,
        order,
      } as SortSearch;

      if (property && order) {
        value.property = property;
      }

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
      .join("+");
  }
}
