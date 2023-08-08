import { DatasetRepository } from "~/v1/infrastructure/repositories";

export class DeleteDatasetUseCase {
  constructor(private readonly datasetRepository: DatasetRepository) {}

  async execute(datasetId: string) {
    await this.datasetRepository.delete(datasetId);
  }
}
