import { Dataset } from "../entities/Dataset";

export interface IDatasetRepository {
  getAll(): Promise<Dataset[]>;
}
