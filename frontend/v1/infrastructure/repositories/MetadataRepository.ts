import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendMetadata, Response } from "../types";
const RECORD_API_ERRORS = {
  ERROR_FETCHING_METADATA: "ERROR_FETCHING_METADATA",
};

export class MetadataRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getMetadataFilters(datasetId: string) {
    try {
      const url = `/v1/me/datasets/${datasetId}/metadata-properties`;

      const { data } = await this.axios.get<Response<BackendMetadata[]>>(url);

      return data.items;
    } catch (err) {
      throw {
        response: RECORD_API_ERRORS.ERROR_FETCHING_METADATA,
      };
    }
  }
}
