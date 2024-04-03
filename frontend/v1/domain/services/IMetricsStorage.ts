import { Metrics } from "../entities/dataset/Metrics";

export interface IMetricsStorage {
  save(metrics: Metrics);
}
