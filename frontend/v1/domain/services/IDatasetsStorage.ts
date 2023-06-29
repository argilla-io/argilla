import { Dataset } from "../entities/Dataset";

export interface IDatasetsStorage {
  save(datasets: Dataset[]): void;
}
