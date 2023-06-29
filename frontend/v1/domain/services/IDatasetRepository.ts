import { Dataset } from "../entities/Dataset";

export interface IDatasetRepository {
  getById(id: string): Promise<Dataset>;
  getAll(): Promise<Dataset[]>;
}
