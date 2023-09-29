import { Metadata } from "./Metadata";

class MetadataSort {
  public selected = false;
  public sort: "asc" | "desc" = "asc";
  constructor(private metadata: Metadata | { name: string }) {}

  get name() {
    return this.metadata.name;
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
    return this.metadataSorts.filter((metadataSort) => !metadataSort.selected);
  }

  get selectedCategoriesName() {
    return this.selectedCategories.map((metadataSort) => metadataSort.name);
  }

  select(category: string) {
    const found = this.findByCategory(category);
    if (found) {
      found.selected = true;
      this.selectedCategories.push(found);
    }
  }

  unselect(category: string) {
    const indexOf = this.selectedCategories.findIndex(
      (metadataSort) => metadataSort.name === category
    );

    if (indexOf > -1) {
      this.selectedCategories[indexOf].selected = false;
      this.selectedCategories.splice(indexOf, 1);
    }
  }

  replace(category: string, newCategory: string) {
    const oldCategory = this.findByCategory(category);
    oldCategory.selected = false;

    const newCategoryFound = this.findByCategory(newCategory);
    newCategoryFound.selected = true;

    const indexOf = this.selectedCategories.findIndex(
      (metadataSort) => metadataSort.name === category
    );

    if (indexOf > -1) {
      this.selectedCategories[indexOf] = newCategoryFound;
    }
  }

  clear() {
    this.selectedCategories.forEach((metadataSort) => {
      metadataSort.selected = false;
    });
    this.selectedCategories = [];
  }

  toggleSort(category: string) {
    const found = this.findByCategory(category);
    if (found) found.sort = found.sort === "asc" ? "desc" : "asc";
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
        found.selected = true;
        found.sort = sort as "asc" | "desc";

        this.selectedCategories.push(found);
      }
    });
  }

  private findByCategory(category: string) {
    return this.metadataSorts.find((m) => m.name === category);
  }
}
