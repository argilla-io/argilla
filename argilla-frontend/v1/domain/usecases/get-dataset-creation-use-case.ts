import { DatasetCreationBuilder } from "../entities/hub/dataset-creation";
import { HubRepository } from "~/v1/infrastructure/repositories/HubRepository";

export class GetDatasetCreationUseCase {
  constructor(private readonly hubRepository: HubRepository) {}

  async execute(repoId: string) {
    const datasetInfo = await this.hubRepository.getDatasetCreation(repoId);

    const datasetCreation = new DatasetCreationBuilder(
      datasetInfo.dataset_info
    );
    return datasetCreation.build();
  }
}
