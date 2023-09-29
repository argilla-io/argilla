import { Metadata } from "./Metadata";

interface OptionForFilter {
  selected: boolean;
  label: string;
}
interface RangeValue {
  ge: number;
  le: number;
}

class MetadataFilter {
  public value: RangeValue;
  public options: OptionForFilter[];

  constructor(private metadata: Metadata) {
    if (this.isTerms) {
      this.options = this.settings.values.map((value: string) => {
        return { selected: false, label: value };
      });
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

  get isTerms() {
    return this.metadata.isTerms;
  }

  get settings() {
    return this.metadata.settings;
  }

  get hasValues() {
    if (this.isTerms) return this.options.length > 0;

    return (
      (this.value.ge === 0 || !!this.value.ge) &&
      (this.value.le === 0 || !!this.value.le)
    );
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
    return this.getFilterSelected().map((cat) => cat.name);
  }

  findByCategory(category: string) {
    return this.metadata.find((cat) => cat.name === category);
  }

  convertToRouteParam(): string[] {
    return this.toQueryParams().map((metadata) => {
      return `${metadata.name}:${metadata.value}`;
    });
  }

  completeByRouteParams(params = "") {
    this.metadata.forEach((m) => m.clear());

    if (!params) return;

    const metadataFilter = params.split("+").map((metadata) => {
      const [name, value] = metadata.split(/:(.*)/s);
      return { name, value };
    });

    metadataFilter.forEach(({ name, value }) => {
      this.findByCategory(name)?.completeMetadata(value);
    });
  }

  private getFilterSelected() {
    return this.metadata.filter((m) => m.isAnswered);
  }

  private toQueryParams() {
    return this.getFilterSelected().map((m) => {
      return {
        name: m.name,
        value: m.isTerms
          ? m.selectedOptions.map((s) => s.label).join(",")
          : JSON.stringify(m.value),
      };
    });
  }
}
