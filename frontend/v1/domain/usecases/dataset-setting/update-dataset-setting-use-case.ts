import { Dataset } from "../../entities/Dataset";
import { DatasetRepository } from "~/v1/infrastructure/repositories";

export class UpdateDatasetSettingUseCase {
  constructor(private readonly datasetRepository: DatasetRepository) {}

  async execute(dataset: Dataset) {
    const response = await this.datasetRepository.update(dataset);

    dataset.update(response.when);
  }
}
