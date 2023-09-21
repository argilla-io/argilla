import { MetadataRepository } from "~/v1/infrastructure/repositories/MetadataRepository";

export class GetMetadataFiltersUseCase {
  constructor(private readonly metadataRepository: MetadataRepository) {}

  execute(datasetId: string) {
    return this.metadataRepository.getMetadataFilters(datasetId);
  }
}
