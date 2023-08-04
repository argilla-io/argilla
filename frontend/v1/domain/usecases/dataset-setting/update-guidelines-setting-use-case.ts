import { Dataset } from "../../entities/Dataset";
import { DatasetRepository } from "~/v1/infrastructure/repositories";

export class UpdateGuidelinesSettingUseCase {
  constructor(private readonly datasetRepository: DatasetRepository) {}

  async execute(dataset: Dataset) {
    await this.datasetRepository.update(dataset);
  }
}
