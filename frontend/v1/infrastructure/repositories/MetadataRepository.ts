import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendMetadata, Response } from "../types";
import { MetadataMetricsRepository } from "./MetadataMetricsRepository";
const RECORD_API_ERRORS = {
  ERROR_FETCHING_METADATA: "ERROR_FETCHING_METADATA",
};

export class MetadataRepository {
  private readonly metadataMetricsRepository: MetadataMetricsRepository;
  constructor(private readonly axios: NuxtAxiosInstance) {
    this.metadataMetricsRepository = new MetadataMetricsRepository(axios);
  }

  async getMetadataFilters(datasetId: string) {
    try {
      const url = `/v1/datasets/${datasetId}/metadata-properties`;

      const { data } = await this.axios.get<Response<BackendMetadata[]>>(url);

      return this.completeEmptyMetadataFilters(data.items);
    } catch (err) {
      throw {
        response: RECORD_API_ERRORS.ERROR_FETCHING_METADATA,
      };
    }
  }

  private async completeEmptyMetadataFilters(
    metadataFilters: BackendMetadata[]
  ): Promise<BackendMetadata[]> {
    const metadataWithNoValues = metadataFilters.filter((m) => {
      if (m.settings.type === "terms") {
        return !m.settings.values;
      }

      return m.settings.max === null && m.settings.min === null;
    });

    const metrics = await Promise.allSettled(
      metadataWithNoValues.map((m) =>
        this.metadataMetricsRepository.getMetric(m.id)
      )
    );

    metrics.forEach((response) => {
      if (response.status === "rejected") return;
      const metric = response.value;

      const metadata = metadataFilters.find((m) => m.id === metric.id);

      if (metadata.settings.type === "terms") {
        metadata.settings.values = metric.values.map((item) => item.term);
      } else {
        metadata.settings.max = metric.max!;
        metadata.settings.min = metric.min!;
      }
    });

    return metadataFilters;
  }
}
