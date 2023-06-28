import { IDatasetRepository } from "../services/IDatasetRepository";
import { IDatasetStorage } from "../services/IDatasetStorage";

export class GetDatasetsUseCase {
  constructor(
    private readonly datasetRepository: IDatasetRepository,
    private readonly datasetStorage: IDatasetStorage
  ) {}

  async execute() {
    const datasets = await this.datasetRepository.getAll();

    this.datasetStorage.save(datasets);
  }
}
