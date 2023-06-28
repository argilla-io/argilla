import { Dataset } from "../entities/Dataset";

export interface IDatasetStorage {
  save(datasets: Dataset[]): void;
}
