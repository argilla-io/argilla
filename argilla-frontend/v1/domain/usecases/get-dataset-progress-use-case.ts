import { IDatasetRepository } from "../services/IDatasetRepository";

export class GetDatasetProgressUseCase {
  constructor(private readonly datasetRepository: IDatasetRepository) {}

  execute(datasetId: string) {
    return this.datasetRepository.getProgress(datasetId);
  }
}
