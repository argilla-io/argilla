import { metadataMocked } from "../entities/__mocks__/metadata/mock";
import { Metadata } from "../entities/metadata/Metadata";
import { MetadataFilter } from "../entities/metadata/MetadataFilter";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";
import { MetadataRepository } from "~/v1/infrastructure/repositories/MetadataRepository";

export class MetadataRepositoryMocked extends MetadataRepository {
  constructor() {
    super(null as any);
  }

  async getMetadataFilters(_: string): Promise<any> {
    const debounce = useDebounce(400);

    await debounce.wait();

    return metadataMocked;
  }
}

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
