import { Metadata } from "./Metadata";

export class MetadataFilter {
  constructor(private readonly metadata: Metadata[]) {}

  get categories() {
    return this.metadata.map((cat) => cat.name);
  }

  findByCategory(category: string) {
    return this.metadata.find((cat) => cat.name === category);
  }
}
