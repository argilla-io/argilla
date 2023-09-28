import { Metadata } from "../entities/metadata/Metadata";
import { MetadataFilter } from "../entities/metadata/MetadataFilter";
import { MetadataRepository } from "~/v1/infrastructure/repositories/MetadataRepository";

export class GetMetadataFiltersUseCase {
  constructor(private readonly metadataRepository: MetadataRepository) {}

  async execute(datasetId: string): Promise<MetadataFilter> {
    const filters = await this.metadataRepository.getMetadataFilters(datasetId);

    const metadataFilters = filters.map((metadata) => {
      return new Metadata(
        metadata.id,
        metadata.name,
        metadata.description,
        metadata.settings
      );
    });

    return new MetadataFilter(metadataFilters);
  }
}
