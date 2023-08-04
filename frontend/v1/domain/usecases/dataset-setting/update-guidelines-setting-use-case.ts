import { DatasetRepository } from "~/v1/infrastructure/repositories";

export class UpdateGuidelinesSettingUseCase {
  constructor(private readonly datasetRepository: DatasetRepository) {}

  async execute(datasetId: string, newGuidelines: string) {
    await this.datasetRepository.updateGuidelines(datasetId, newGuidelines);
  }
}
