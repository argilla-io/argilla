import { DatasetCreation } from "../entities/hub/DatasetCreation";
import { HubRepository } from "~/v1/infrastructure/repositories";

export class GetFirstRecordFromHub {
  constructor(private readonly hubRepository: HubRepository) {}

  execute(dataset: DatasetCreation) {
    return this.hubRepository.getFirstRecord(
      dataset.repoId,
      dataset.selectedSubset.selectedSplit.name
    );
  }
}
