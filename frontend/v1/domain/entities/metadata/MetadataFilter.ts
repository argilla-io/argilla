import { Metadata } from "./Metadata";

export class MetadataFilter {
  constructor(private readonly metadata: Metadata[]) {}

  get categories() {
    return this.metadata.map((cat) => cat.name);
  }

  findByCategory(category: string) {
    return this.metadata.find((cat) => cat.name === category);
  }

  convertToRouteParam() {
    return this.toQueryParams().map((metadata) => {
      return `${metadata.name}:${metadata.value}`;
    });
  }

  completeByRouteParams(params: string) {
    if (!params) return;

    const metadataFilter = params.split("+").map((metadata) => {
      const [name, value] = metadata.split(":");
      return { name, value };
    });

    metadataFilter.forEach(({ name, value }) => {
      this.findByCategory(name)?.completeMetadata(value);
    });
  }

  private toQueryParams() {
    return this.metadata.map((m) => {
      return {
        name: m.name,
        value: m.isTerms
          ? m.selectedOptions.map((s) => s.label).join(",")
          : "TBD",
      };
    });
  }
}
