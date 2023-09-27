import { Metadata } from "./Metadata";

export class MetadataFilter {
  constructor(private readonly metadata: Metadata[]) {}

  get hasFilters() {
    return this.metadata.length > 0;
  }

  get categories() {
    return this.metadata.map((cat) => cat.name);
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
