import { Subset } from "./Subset";

export class DatasetCreation {
  public selectedSubset: Subset;

  public readonly firstRecord: {};

  constructor(
    public readonly repoId: string,
    public name: string,
    private readonly subset: Subset[]
  ) {
    this.selectedSubset = subset[0];
  }

  changeSubset(name: string) {
    this.selectedSubset = this.subset.find((s) => s.name === name);
  }

  get hasMoreThanOneSubset() {
    return this.subset.length > 1;
  }

  get subsets() {
    return this.subset.map((s) => s.name);
  }

  get fields() {
    return this.selectedSubset.fields;
  }

  get questions() {
    return this.selectedSubset.questions;
  }

  get metadata() {
    return this.selectedSubset.metadata;
  }

  get columns() {
    return this.selectedSubset.columns;
  }
}
