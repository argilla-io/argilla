import { Metadata } from "./Metadata";

interface OptionForFilter {
  selected: boolean;
  label: string;
}
interface RangeValue {
  ge?: number;
  le?: number;
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

  get hasValues() {
    if (this.isTerms) return this.options.length > 0;

    return this.value.ge !== null && this.value.le !== null;
  }

  public filterByText(text: string) {
    return this.options.filter((option) =>
      option.label.toLowerCase().includes(text.toLowerCase())
    );
  }

  public get isAnswered(): boolean {
    return this.isTerms
      ? this.selectedOptions.length > 0
      : this.value.ge !== this.settings.min ||
          this.value.le !== this.settings.max;
  }

  public get selectedOptions(): OptionForFilter[] {
    return this.options.filter((option) => option.selected);
  }

  public completeMetadata(value: string) {
    if (this.isTerms) {
      value.split(",").forEach((label) => {
        const option = this.options.find((option) => option.label === label);
        if (option) option.selected = true;
      });
    } else {
      try {
        const { ge, le } = JSON.parse(value);
        this.value.ge = ge;
        this.value.le = le;
      } catch (error) {
        this.value.ge = this.settings.min;
        this.value.le = this.settings.max;
      }
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
  private latestCommit: string[] = [];

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

    return this.hasChangesSinceLatestCommitWith(this.convertToRouteParam());
  }

  get filteredCategories() {
    return this.filteredMetadata;
  }

  findByCategory(category: string) {
    return this.metadata.find((cat) => cat.name === category);
  }

  hasChangesSinceLatestCommitWith(compare: string[]) {
    return this.latestCommit.join("") !== compare.join("");
  }

  commit(): string[] {
    this.synchronizeFilteredMetadata();

    this.latestCommit = this.convertToRouteParam();

    return this.latestCommit;
  }

  initializeWith(params: string[]) {
    this.metadata.forEach((m) => m.clear());

    if (!params.length) return;

    const metadataFilter = params.map((metadata) => {
      const [name, value] = metadata.split(/:(.*)/s);
      return { name, value };
    });

    metadataFilter.forEach(({ name, value }) => {
      const metadata = this.findByCategory(name);
      if (metadata) {
        metadata.completeMetadata(value);

        if (this.filteredMetadata.includes(metadata)) return;

        this.filteredMetadata.push(metadata);
      }
    });

    this.commit();
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

  private convertToRouteParam(): string[] {
    return this.toQueryParams().map((metadata) => {
      return `${metadata.name}:${metadata.value}`;
    });
  }

  private toQueryParams() {
    return this.filteredMetadata.map((m) => {
      return {
        name: m.name,
        value: m.isTerms
          ? m.selectedOptions.map((s) => s.label).join(",")
          : JSON.stringify(m.value),
      };
    });
  }
}
