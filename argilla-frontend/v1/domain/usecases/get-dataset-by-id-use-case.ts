import { IDatasetRepository } from "../services/IDatasetRepository";
import { IDatasetStorage } from "../services/IDatasetStorage";

export class GetDatasetByIdUseCase {
  constructor(
    private readonly datasetRepository: IDatasetRepository,
    private readonly datasetStorage: IDatasetStorage
  ) {}

  async execute(id: string) {
    const dataset = await this.datasetRepository.getById(id);

    this.datasetStorage.save(dataset);
  }
}
