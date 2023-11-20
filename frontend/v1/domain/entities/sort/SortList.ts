import { Metadata } from "../metadata/Metadata";

const SORT_ASC = "asc";
const SORT_DESC = "desc";

type SortOptions = "asc" | "desc";

export interface SortSearch {
  key: string;
  name: string;
  sort: SortOptions;
}

abstract class Sort {
  public sort: SortOptions = SORT_ASC;

  constructor(public readonly key: string = "") {}

  toggleSort() {
    this.sort = this.sort === SORT_ASC ? SORT_DESC : SORT_ASC;
  }

  abstract get name(): string;

  abstract get title(): string;

  abstract get canSort(): boolean;
}

class MetadataSort extends Sort {
  constructor(private metadata: Metadata) {
    super("metadata");
  }

  get name() {
    return this.metadata.name;
  }

  get title() {
    return this.metadata.title;
  }

  get canSort(): boolean {
    return this.metadata.hasValues;
  }
}

class RecordSort extends Sort {
  constructor(public readonly name: string, public readonly title = name) {
    super();
  }

  get canSort(): boolean {
    return true;
  }
}

export class SortList {
  private metadataSorts: Sort[];
  private selectedCategories: Sort[] = [];
  private latestCommit: SortSearch[] = [];

  constructor(metadata: Metadata[] = []) {
    this.metadataSorts = metadata.map((metadata) => new MetadataSort(metadata));
    this.metadataSorts.push(new RecordSort("inserted_at"));
    this.metadataSorts.push(new RecordSort("updated_at"));
  }

  get selected() {
    return this.selectedCategories;
  }

  get noSelected() {
    return this.metadataSorts.filter(
      (metadata) => !this.selectedCategories.includes(metadata)
    );
  }

  select(category: string) {
    const found = this.findByCategory(category);

    if (found) {
      this.selectedCategories.push(found);
    }
  }

  unselect(category: string) {
    const indexOf = this.selectedCategories.findIndex(
      (metadataSort) => metadataSort.name === category
    );

    if (indexOf > -1) {
      this.selectedCategories.splice(indexOf, 1);
    }
  }

  replace(category: string, newCategory: string) {
    const newCategoryFound = this.findByCategory(newCategory);

    const indexOf = this.selectedCategories.findIndex(
      (metadataSort) => metadataSort.name === category
    );

    if (indexOf > -1) {
      this.selectedCategories.splice(indexOf, 1, newCategoryFound);
    }
  }

  clear() {
    this.selectedCategories = [];
  }

  toggleSort(category: string) {
    const found = this.findByCategory(category);
    if (found) found.toggleSort();
  }

  get hasChanges() {
    return this.hasDifferencesWith(this.createSortCriteria());
  }

  hasDifferencesWith(compare: SortSearch[]) {
    return JSON.stringify(this.latestCommit) !== JSON.stringify(compare);
  }

  commit(): SortSearch[] {
    this.latestCommit = this.createSortCriteria();

    return this.latestCommit;
  }

  private createSortCriteria(): SortSearch[] {
    return this.selectedCategories.map((metadataSort) => {
      return {
        key: metadataSort.key,
        name: metadataSort.name,
        sort: metadataSort.sort,
      };
    });
  }

  complete(sort: SortSearch[]) {
    if (!this.hasDifferencesWith(sort)) return;

    this.clear();

    if (!sort.length) return;

    sort.forEach(({ name, sort }) => {
      const found = this.findByCategory(name);

      if (found) {
        found.sort = sort;

        this.selectedCategories.push(found);
      }
    });

    this.commit();
  }

  private findByCategory(category: string) {
    return this.metadataSorts.find((m) => m.name === category);
  }
}
