import { Dataset } from "../entities/dataset/Dataset";
import { Progress } from "../entities/dataset/Progress";
import { DatasetCreation } from "../entities/hub/DatasetCreation";

export type DatasetId = string;
export type JobId = string;

export interface IDatasetRepository {
  create(dataset: DatasetCreation): Promise<DatasetId>;
  publish(datasetId: string): Promise<boolean>;
  import(datasetId: DatasetId, creation: DatasetCreation): Promise<JobId>;
  getById(id: string): Promise<Dataset>;
  getAll(): Promise<Dataset[]>;
  delete(datasetId: string);
  update(dataset: Partial<Dataset>): Promise<{ when: string }>;
  getProgress(datasetId: string): Promise<Progress>;
}
