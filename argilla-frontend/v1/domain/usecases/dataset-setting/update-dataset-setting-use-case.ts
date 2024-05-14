import { Dataset } from "../../entities/dataset/Dataset";
import { IDatasetRepository } from "../../services/IDatasetRepository";

export class UpdateDatasetSettingUseCase {
  constructor(private readonly datasetRepository: IDatasetRepository) {}

  async execute(dataset: Dataset) {
    const response = await this.datasetRepository.update(dataset);

    dataset.update(response.when);
  }
}
