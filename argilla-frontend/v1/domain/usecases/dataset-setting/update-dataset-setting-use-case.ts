import { Dataset } from "../../entities/dataset/Dataset";
import { IDatasetRepository } from "../../services/IDatasetRepository";

export class UpdateDatasetSettingUseCase {
  constructor(private readonly datasetRepository: IDatasetRepository) {}

  async execute(
    dataset: Dataset,
    part: "guidelines" | "metadata" | "distribution"
  ) {
    try {
      const response = await this.update(dataset, part);
      dataset.update(response.when, part);
    } catch (e) {
      this.restore(dataset, part);
    }
  }

  private update(
    dataset: Dataset,
    part: "guidelines" | "metadata" | "distribution"
  ) {
    if (part === "guidelines")
      return this.datasetRepository.update({
        id: dataset.id,
        guidelines: dataset.guidelines,
      });

    if (part === "metadata")
      return this.datasetRepository.update({
        id: dataset.id,
        allowExtraMetadata: dataset.allowExtraMetadata,
      });

    if (part === "distribution")
      return this.datasetRepository.update({
        id: dataset.id,
        distribution: dataset.distribution,
      });
  }

  private restore(
    dataset: Dataset,
    part: "guidelines" | "metadata" | "distribution"
  ) {
    if (part === "guidelines") dataset.restoreGuidelines();

    if (part === "metadata") dataset.restoreMetadata();

    if (part === "distribution") dataset.restoreDistribution();
  }
}
