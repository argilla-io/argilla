import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendMetadataMetric } from "../types";

const RECORD_API_ERRORS = {
  ERROR_FETCHING_METADATA_METRIC: "ERROR_FETCHING_METADATA_METRIC",
};

export class MetadataMetricsRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getMetric(metadataId: string): Promise<BackendMetadataMetric> {
    try {
      const { data } = await this.axios.get<BackendMetadataMetric>(
        `/v1/metadata-properties/${metadataId}/metrics`,
        { headers: { "cache-control": "max-age=120" } }
      );

      return {
        id: metadataId,
        ...data,
      };
    } catch (err) {
      throw {
        response: RECORD_API_ERRORS.ERROR_FETCHING_METADATA_METRIC,
      };
    }
  }
}
