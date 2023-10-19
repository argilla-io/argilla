export interface DatasetVector {
  id: string;
  title: string;
}

export class DatasetVectorsRepositoryMock {
  async getVectors(_datasetId: string) {
    const vectors = await Promise.all([
      { id: "1", title: "Vector 1" },
      { id: "2", title: "Vector 2" },
    ]);

    return vectors;
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
