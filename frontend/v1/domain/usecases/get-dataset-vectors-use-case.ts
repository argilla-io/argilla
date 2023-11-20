import { DatasetVector } from "../entities/vector/DatasetVector";
import { VectorRepository } from "@/v1/infrastructure/repositories/VectorRepository";

export class GetDatasetVectorsUseCase {
  constructor(private readonly vectorRepository: VectorRepository) {}

  execute(datasetId: string): Promise<DatasetVector[]> {
    return this.vectorRepository.getVectors(datasetId);
  }
}
