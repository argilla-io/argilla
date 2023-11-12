import { OptionForFilter, RangeValue } from "../common/Filter";
import { Metadata } from "./Metadata";

export interface MetadataSearch {
  name: string;
  value: string[] | RangeValue;
}

class MetadataFilter {
  public value: RangeValue;
  public options: OptionForFilter[] = [];
  constructor(private metadata: Metadata) {
    if (this.isTerms) {
      this.options =
        this.settings.values?.map((value: string) => {
          return { selected: false, label: value };
        }) ?? [];
    } else {
      this.value = {
        ge: this.settings.min,
        le: this.settings.max,
      };
    }
  }

  get name() {
    return this.metadata.name;
  }

  get title() {
    return this.metadata.title;
  }

  get isTerms() {
    return this.metadata.isTerms;
  }

  get settings() {
    return this.metadata.settings;
  }

  get canFilter() {
    return this.metadata.hasValues;
  }

  filterByText(text: string) {
    return this.options.filter((option) =>
      option.label.toLowerCase().includes(text.toLowerCase())
    );
  }

  get isAnswered(): boolean {
    return this.isTerms
      ? this.selectedOptions.length > 0
      : this.value.ge !== this.settings.min ||
          this.value.le !== this.settings.max;
  }

  get selectedOptions(): OptionForFilter[] {
    return this.options.filter((option) => option.selected);
  }

  completeMetadata(value: string[] | RangeValue) {
    if (!value) return;

    if (this.isTerms) {
      const labels = value as string[];
      labels.forEach((label) => {
        const option = this.options.find((option) => option.label === label);
        if (option) option.selected = true;
      });
    } else {
      const { ge, le } = value as RangeValue;

      this.value.ge = ge;
      this.value.le = le;
    }
  }

  clear(): void {
    if (this.isTerms) return this.options.forEach((o) => (o.selected = false));

    this.value.ge = this.settings.min;
    this.value.le = this.settings.max;
  }
}

export class MetadataFilterList {
  private readonly metadata: MetadataFilter[];
  private readonly filteredMetadata: MetadataFilter[] = [];
  private latestCommit: MetadataSearch[] = [];

  constructor(metadata: Metadata[]) {
    this.metadata = metadata.map((m) => new MetadataFilter(m));
  }

  get hasFilters() {
    return this.metadata.length > 0;
  }

  get categories() {
    return this.metadata;
  }

  get filtered() {
    return this.metadata.filter((m) => m.isAnswered);
  }

  get hasChangesSinceLatestCommit() {
    if (this.filteredMetadata.length !== this.filtered.length) return true;

    if (this.filtered.some((f) => !this.filteredMetadata.includes(f)))
      return true;

    return this.hasChangesSinceLatestCommitWith(this.createCommit());
  }

  get filteredCategories() {
    return this.filteredMetadata;
  }

  hasChangesSinceLatestCommitWith(compare: MetadataSearch[]) {
    return JSON.stringify(this.latestCommit) !== JSON.stringify(compare);
  }

  commit(): MetadataSearch[] {
    this.synchronizeFilteredMetadata();

    this.latestCommit = this.createCommit();

    return this.latestCommit;
  }

  complete(params: MetadataSearch[]) {
    if (!this.hasChangesSinceLatestCommitWith(params)) return;

    this.metadata.forEach((m) => m.clear());

    if (!params.length) return;

    params.forEach(({ name, value }) => {
      const metadata = this.findByCategory(name);

      if (metadata) {
        metadata.completeMetadata(value);

        if (this.filteredMetadata.includes(metadata)) return;

        this.filteredMetadata.push(metadata);
      }
    });

    this.commit();
  }

  private createCommit(): MetadataSearch[] {
    return this.filteredMetadata.map((metadata) => {
      return {
        name: metadata.name,
        value: metadata.isTerms
          ? metadata.selectedOptions.map((s) => s.label)
          : {
              ge: metadata.value.ge,
              le: metadata.value.le,
            },
      };
    });
  }

  private findByCategory(category: string) {
    return this.metadata.find((cat) => cat.name === category);
  }

  private synchronizeFilteredMetadata() {
    const newFiltered = this.filtered.filter(
      (category) => !this.filteredMetadata.includes(category)
    );
    newFiltered.forEach((f) => {
      this.filteredMetadata.push(f);
    });

    const removedFilters = this.filteredMetadata.filter(
      (category) => !this.filtered.includes(category)
    );
    removedFilters.forEach((f) => {
      const indexOf = this.filteredMetadata.indexOf(f);

      this.filteredMetadata.splice(indexOf, 1);
    });
  }
}
