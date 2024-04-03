import { Dataset } from "../entities/dataset/Dataset";
import { Progress } from "../entities/dataset/Progress";

export interface IDatasetRepository {
  getById(id: string): Promise<Dataset>;
  getAll(): Promise<Dataset[]>;
  delete(datasetId: string);
  update({ id, allowExtraMetadata, guidelines }: Dataset);
  getProgress(datasetId: string): Promise<Progress>;
}
