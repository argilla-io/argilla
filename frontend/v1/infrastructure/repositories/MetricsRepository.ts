import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Metrics } from "~/v1/domain/entities/Metrics";

interface BackendMetrics {
  records: {
    count: number;
  };
  responses: {
    count: number;
    submitted: number;
    discarded: number;
    draft: number;
  };
}

export class MetricsRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getMetrics(datasetId: string): Promise<Metrics> {
    try {
      const { data } = await this.axios.get<BackendMetrics>(
        `/v1/me/datasets/${datasetId}/metrics`
      );

      return new Metrics(
        data.records.count,
        data.responses.count,
        data.responses.submitted,
        data.responses.discarded,
        data.responses.draft
      );
    } catch {
      /* lint:disable:no-empty */
    }
  }
}
