import { Dataset } from "../entities/dataset/Dataset";

export interface IDatasetStorage {
  save(dataset: Dataset): void;
}
