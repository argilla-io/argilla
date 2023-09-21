import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Response } from "../types";
const RECORD_API_ERRORS = {
  ERROR_FETCHING_METADATA: "ERROR_FETCHING_METADATA",
};

interface MetadataTermsSettings {
  type: "terms";
  values?: string[];
}
interface MetadataIntegerSettings {
  type: "integer";
}

interface MetadataFloatSettings {
  type: "float";
}

interface BackendMetadata {
  id: string;
  name: string;
  description: string;
  settings:
    | MetadataTermsSettings
    | MetadataIntegerSettings
    | MetadataFloatSettings;
}

export class MetadataRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getMetadataFilters(datasetId: string) {
    try {
      const url = `/v1/me/datasets/${datasetId}/metadata`;

      const { data } = await this.axios.get<Response<BackendMetadata[]>>(url);

      return data.items;
    } catch (err) {
      throw {
        response: RECORD_API_ERRORS.ERROR_FETCHING_METADATA,
      };
    }
  }
}
