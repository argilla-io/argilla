import { Dataset } from "../entities/dataset/Dataset";
import { Progress } from "../entities/dataset/Progress";

export interface IDatasetRepository {
  getById(id: string): Promise<Dataset>;
  getAll(): Promise<Dataset[]>;
  delete(datasetId: string);
  update(dataset: Partial<Dataset>): Promise<{ when: string }>;
  getProgress(datasetId: string): Promise<Progress>;
}
