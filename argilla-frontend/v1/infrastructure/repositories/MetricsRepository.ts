import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { largeCache } from "./AxiosCache";
import { Metrics } from "~/v1/domain/entities/dataset/Metrics";

interface BackendMetrics {
  responses: {
    total: number;
    submitted: number;
    discarded: number;
    draft: number;
    pending: number;
  };
}

export class MetricsRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getMetrics(datasetId: string): Promise<Metrics> {
    try {
      const { data } = await this.axios.get<BackendMetrics>(
        `/v1/me/datasets/${datasetId}/metrics`,
        largeCache()
      );

      return new Metrics(
        data.responses.total,
        data.responses.submitted,
        data.responses.discarded,
        data.responses.draft,
        data.responses.pending
      );
    } catch {
      /* lint:disable:no-empty */
    }
  }
}
