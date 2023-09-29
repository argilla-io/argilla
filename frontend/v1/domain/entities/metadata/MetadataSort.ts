import { Metadata } from "./Metadata";

type SortOptions = "asc" | "desc";

interface HardcodeMetadata {
  name: string;
}

class MetadataSort {
  public sort: SortOptions = "asc";
  constructor(private metadata: Metadata | HardcodeMetadata) {}

  get name() {
    return this.metadata.name;
  }

  toggleSort() {
    this.sort = this.sort === "asc" ? "desc" : "asc";
  }
}

export class MetadataSortList {
  private metadataSorts: MetadataSort[];
  private selectedCategories: MetadataSort[] = [];
  constructor(metadata: Metadata[] = []) {
    this.metadataSorts = metadata.map((metadata) => new MetadataSort(metadata));
    this.metadataSorts.push(new MetadataSort({ name: "inserted_at" }));
    this.metadataSorts.push(new MetadataSort({ name: "updated_at" }));
  }

  get selected() {
    return this.selectedCategories;
  }

  get noSelected() {
    return this.metadataSorts.filter(
      (metadata) => !this.selectedCategories.includes(metadata)
    );
  }

  get selectedCategoriesName() {
    return this.selectedCategories.map((metadataSort) => metadataSort.name);
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

  convertToRouteParam(): string[] {
    return this.selected.map((c) => `metadata.${c.name}:${c.sort}`);
  }

  completeByRouteParams(sort: string) {
    this.clear();

    if (!sort) return;

    const sortParams = sort.replaceAll("metadata.", "").split(",");

    sortParams.forEach((sortParam) => {
      const [name, sort] = sortParam.split(":");
      const found = this.findByCategory(name);
      if (found) {
        found.sort = sort as SortOptions;

        this.selectedCategories.push(found);
      }
    });
  }

  private findByCategory(category: string) {
    return this.metadataSorts.find((m) => m.name === category);
  }
}
