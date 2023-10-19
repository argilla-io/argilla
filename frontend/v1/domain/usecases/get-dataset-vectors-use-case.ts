export interface DatasetVector {
  id: string;
}

export class DatasetVectorsRepositoryMock {
  getVectors(datasetId: string) {
    return Promise.all([{ id: "text_vector" }, { id: "second_vector" }]);
  }
}

export class GetDatasetVectorsUseCase {
  constructor(
    private readonly datasetVectorsRepository: DatasetVectorsRepositoryMock
  ) {}

  execute(datasetId: string): Promise<DatasetVector[]> {
    return this.datasetVectorsRepository.getVectors(datasetId);
  }
}
