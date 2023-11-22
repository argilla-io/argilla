import { Criteria } from "../common/Criteria";
import { SortSearch } from "./SortList";

export class SortCriteria extends Criteria {
  public value: SortSearch[] = [];

  get isCompleted(): boolean {
    return this.value.length > 0;
  }

  get urlParams(): string {
    if (!this.isCompleted) return "";

    return JSON.stringify(this.value);
  }

  complete(urlParams: string) {
    if (!urlParams) return;

    try {
      const sorts = JSON.parse(urlParams) as SortSearch[];

      sorts.forEach((sort) => {
        if (sort.entity && sort.order) this.value.push(sort);
      });
    } catch {
      // Manipulated
    }
  }

  witValue(value: SortSearch[]) {
    this.value = value.map((v) => ({ ...v }));
  }

  reset() {
    this.value = [];
  }
}
