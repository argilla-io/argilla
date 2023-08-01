import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendField, Response } from "../types/";

export class FieldRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getFields(datasetId: string): Promise<BackendField[]> {
    try {
      const { data } = await this.axios.get<Response<BackendField[]>>(
        `/v1/datasets/${datasetId}/fields`
      );

      return data.items;
    } catch (err) {
      throw {
        response: "ERROR_FETCHING_FIELDS",
      };
    }
  }
}
