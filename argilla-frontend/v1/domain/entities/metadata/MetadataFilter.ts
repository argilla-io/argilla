import { OptionForFilter, RangeValue } from "../common/Filter";
import { Metadata } from "./Metadata";

export interface MetadataSearch {
  name: string;
  value: string[] | RangeValue;
}

// TODO: Add base class to support two types of filter, like a SuggestionFilter.ts
class MetadataFilter {
  public rangeValue: RangeValue;
  public options: OptionForFilter[] = [];
  constructor(private metadata: Metadata) {
    if (this.isTerms) {
      this.options =
        this.settings.values?.map((value: string) => {
          return { selected: false, value };
        }) ?? [];
    } else {
      this.rangeValue = {
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

  get isInteger() {
    return this.metadata.isInteger;
  }

  get settings() {
    return this.metadata.settings;
  }

  get canFilter() {
    return this.metadata.hasValues;
  }

  filterByText(text: string) {
    return this.options.filter((option) =>
      option.value.toLowerCase().includes(text.toLowerCase())
    );
  }

  get isAnswered(): boolean {
    return this.isTerms
      ? this.selectedOptions.length > 0
      : this.rangeValue.ge !== this.settings.min ||
          this.rangeValue.le !== this.settings.max;
  }

  get selectedOptions(): OptionForFilter[] {
    return this.options.filter((option) => option.selected);
  }

  completeMetadata(value: string[] | RangeValue) {
    if (!value) return;

    if (this.isTerms) {
      // TODO: The base method resolve this
      const labels = value as string[];
      labels.forEach((label) => {
        const option = this.options.find((option) => option.value === label);
        if (option) option.selected = true;
      });
    } else {
      const { ge, le } = value as RangeValue;

      this.rangeValue.ge = ge;
      this.rangeValue.le = le;
    }
  }

  clear(): void {
    if (this.isTerms) return this.options.forEach((o) => (o.selected = false));

    this.rangeValue.ge = this.settings.min;
    this.rangeValue.le = this.settings.max;
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

  get filteredCategories() {
    return this.filteredMetadata;
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

  hasChangesSinceLatestCommitWith(compare: MetadataSearch[]) {
    return JSON.stringify(this.latestCommit) !== JSON.stringify(compare);
  }

  commit(): MetadataSearch[] {
    this.synchronizeFiltered();

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
          ? metadata.selectedOptions.map((s) => s.value)
          : {
              ge: metadata.rangeValue.ge,
              le: metadata.rangeValue.le,
            },
      };
    });
  }

  private findByCategory(category: string) {
    return this.metadata.find((cat) => cat.name === category);
  }

  private synchronizeFiltered() {
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
