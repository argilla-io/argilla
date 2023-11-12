import { Criteria } from "../common/Criteria";
import { SortSearch } from "./MetadataSort";

const SORT_KEY_SEPARATOR = ".";
const ORDER_BY_SEPARATOR = ":";

export class SortCriteria extends Criteria {
  public value: SortSearch[] = [];

  get isCompleted(): boolean {
    return this.value.length > 0;
  }

  get urlParams(): string {
    if (!this.isCompleted) return "";

    return this.value
      .map((c) => `${c.key}${c.name}${ORDER_BY_SEPARATOR}${c.sort}`)
      .join(",");
  }

  get backendParams(): string[] {
    if (!this.isCompleted) return [];

    return this.value.map(
      (c) => `${c.key}${c.name}${ORDER_BY_SEPARATOR}${c.sort}`
    );
  }

  complete(urlParams: string) {
    if (!urlParams) return;

    urlParams.split(",").forEach((sortParam) => {
      const categories = sortParam.split(SORT_KEY_SEPARATOR);
      const [name, sort] =
        categories[categories.length - 1].split(ORDER_BY_SEPARATOR);

      this.value.push({
        key: `${categories[0]}${SORT_KEY_SEPARATOR}`,
        name,
        sort: sort === "asc" ? "asc" : "desc",
      });
    });
  }

  witValue(value: SortSearch[]) {
    this.value = value.map((v) => {
      return {
        key: v.key,
        name: v.name,
        sort: v.sort,
      };
    });
  }

  reset() {
    this.value = [];
  }
}
