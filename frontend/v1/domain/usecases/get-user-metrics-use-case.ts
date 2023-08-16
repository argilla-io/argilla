import { IMetricsStorage } from "../services/IMetricsStorage";
import { MetricsRepository } from "@/v1/infrastructure/repositories/MetricsRepository";

export class GetUserMetricsUseCase {
  constructor(
    private readonly metricsRepository: MetricsRepository,
    private readonly metricsStorage: IMetricsStorage
  ) {}

  async execute(datasetId: string) {
    const metrics = await this.metricsRepository.getMetrics(datasetId);

    this.metricsStorage.save(metrics);
  }
}
