import { IDatasetRepository } from "../services/IDatasetRepository";
import { ITeamProgressStorage } from "../services/ITeamProgressStorage";

export class GetDatasetProgressUseCase {
  constructor(
    private readonly datasetRepository: IDatasetRepository,
    private readonly teamProgress: ITeamProgressStorage
  ) {}

  async execute(datasetId: string) {
    const progress = await this.datasetRepository.getProgress(datasetId);

    this.teamProgress.save(progress);

    return progress;
  }
}
