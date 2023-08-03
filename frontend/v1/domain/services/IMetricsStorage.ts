import { Metrics } from "../entities/Metrics";

export interface IMetricsStorage {
  save(metrics: Metrics);
}
