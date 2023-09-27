import { Metadata } from "../entities/metadata/Metadata";
import { MetadataRepository } from "~/v1/infrastructure/repositories/MetadataRepository";

export class GetMetadataUseCase {
  constructor(private readonly metadataRepository: MetadataRepository) {}

  async execute(datasetId: string): Promise<Metadata[]> {
    const filters = await this.metadataRepository.getMetadataFilters(datasetId);

    const datasetsMetadata = filters.map((metadata) => {
      return new Metadata(
        metadata.id,
        metadata.name,
        metadata.description,
        metadata.settings
      );
    });

    return datasetsMetadata;
  }
}
