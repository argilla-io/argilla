import { Dataset } from "../entities/dataset/Dataset";

export interface IDatasetsStorage {
  save(datasets: Dataset[]): void;
}
