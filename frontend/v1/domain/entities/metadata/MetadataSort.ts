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
  constructor(metadata: Metadata[] = []) {
    this.metadataSorts = metadata.map((metadata) => new MetadataSort(metadata));
    this.metadataSorts.push(new MetadataSort({ name: "inserted_at" }));
    this.metadataSorts.push(new MetadataSort({ name: "updated_at" }));
  }

  get selected() {
    return this.metadataSorts.filter((metadataSort) => metadataSort.selected);
  }

  get noSelected() {
    return this.metadataSorts.filter((metadataSort) => !metadataSort.selected);
  }

  select(category: string) {
    const found = this.metadataSorts.find((m) => m.name === category);
    if (found) found.selected = true;
  }

  unselect(category: string) {
    const found = this.metadataSorts.find((m) => m.name === category);
    if (found) found.selected = false;
  }

  toggleSort(category: string) {
    const found = this.metadataSorts.find((m) => m.name === category);
    if (found) found.sort = found.sort === "asc" ? "desc" : "asc";
  }
}
