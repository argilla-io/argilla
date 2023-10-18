export interface DatasetVector {
  id: string;
}

export class GetDatasetVectorsUseCase {
  execute(datasetId: string): Promise<DatasetVector[]> {
    return Promise.all([{ id: "text_vector" }, { id: "second_vector" }]);
  }
}
