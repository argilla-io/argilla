import { Criteria } from "../common/Criteria";
import { SortSearch } from "./MetadataSort";

const SORT_ELEMENT_SEPARATOR = ",";
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
      .map((c) => {
        if (c.key)
          return `${c.key}${SORT_KEY_SEPARATOR}${c.name}${ORDER_BY_SEPARATOR}${c.sort}`;

        return `${c.name}${ORDER_BY_SEPARATOR}${c.sort}`;
      })
      .join(SORT_ELEMENT_SEPARATOR);
  }

  get backendParams(): string[] {
    if (!this.isCompleted) return [];

    return this.value.map((c) => {
      if (c.key)
        return `${c.key}${SORT_KEY_SEPARATOR}${c.name}${ORDER_BY_SEPARATOR}${c.sort}`;

      return `${c.name}${ORDER_BY_SEPARATOR}${c.sort}`;
    });
  }

  complete(urlParams: string) {
    if (!urlParams) return;

    urlParams.split(SORT_ELEMENT_SEPARATOR).forEach((sortParam) => {
      const sortSearch = this.getSortSearch(sortParam);

      if (sortSearch) this.value.push(sortSearch);
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

  private getSortSearch(sort: string): SortSearch {
    const sortParts = sort.split(ORDER_BY_SEPARATOR);

    if (sortParts.length < 2) return;

    const [rest, sortType] = sortParts;

    const [name, key] = rest.split(SORT_KEY_SEPARATOR, 2).reverse();

    return {
      key,
      name,
      sort: sortType === "asc" ? "asc" : "desc",
    };
  }
}
