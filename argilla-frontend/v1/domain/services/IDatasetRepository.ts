import { Dataset } from "../entities/dataset/Dataset";
import { Progress } from "../entities/dataset/Progress";

export type DatasetId = string;

export interface IDatasetRepository {
  create({ name, workspaceId }): Promise<DatasetId>;
  publish(datasetId: string): Promise<boolean>;
  import({ name, datasetId, subset, split }): Promise<void>;
  getById(id: string): Promise<Dataset>;
  getAll(): Promise<Dataset[]>;
  delete(datasetId: string);
  update(dataset: Partial<Dataset>): Promise<{ when: string }>;
  getProgress(datasetId: string): Promise<Progress>;
}
