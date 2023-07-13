import { Dataset } from "../entities/Dataset";

export interface IDatasetStorage {
  save(dataset: Dataset): void;
}
