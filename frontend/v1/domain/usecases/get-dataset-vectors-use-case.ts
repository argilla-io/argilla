import { VectorRepository } from "@/v1/infrastructure/repositories/VectorRepository";

export interface DatasetVector {
  id: string;
  title: string;
}

export class GetDatasetVectorsUseCase {
  constructor(private readonly vectorRepository: VectorRepository) {}

  execute(datasetId: string): Promise<DatasetVector[]> {
    return this.vectorRepository.getVectors(datasetId);
  }
}
