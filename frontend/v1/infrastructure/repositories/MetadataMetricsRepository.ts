import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendMetadataMetric } from "../types";

const RECORD_API_ERRORS = {
  ERROR_FETCHING_METADATA_METRIC: "ERROR_FETCHING_METADATA_METRIC",
};

export class MetadataMetricsRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getMetric(metadataId: string): Promise<BackendMetadataMetric> {
    try {
      const url = `/v1/metadata-properties/${metadataId}/metrics`;

      const { data } = await this.axios.get<BackendMetadataMetric>(url);

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
