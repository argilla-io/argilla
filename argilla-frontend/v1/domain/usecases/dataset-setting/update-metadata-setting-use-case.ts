import { Metadata } from "../../entities/metadata/Metadata";
import { MetadataRepository } from "~/v1/infrastructure/repositories";

export class UpdateMetadataSettingUseCase {
  constructor(private readonly metadataRepository: MetadataRepository) {}

  async execute(metadata: Metadata) {
    if (!metadata.isValid) {
      throw new Error("Metadata is not valid for update");
    }

    // eslint-disable-next-line camelcase
    const { title, visible_for_annotators } =
      await this.metadataRepository.update(metadata);

    metadata.update(title, visible_for_annotators);
  }
}
