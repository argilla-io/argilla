import { IDatasetRepository } from "../services/IDatasetRepository";

export class DeleteDatasetUseCase {
  constructor(private readonly datasetRepository: IDatasetRepository) {}

  async execute(datasetId: string) {
    await this.datasetRepository.delete(datasetId);
  }
}
