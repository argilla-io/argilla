import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendField, Response } from "../types/";
import { Field } from "~/v1/domain/entities/Field";

export class FieldRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getFields(datasetId: string): Promise<Field[]> {
    try {
      const { data } = await this.axios.get<Response<BackendField[]>>(
        `/v1/datasets/${datasetId}/fields`
      );

      return data.items.map((field) => {
        return new Field(
          field.id,
          field.name,
          field.title,
          datasetId,
          field.required,
          field.settings
        );
      });
    } catch (err) {
      throw {
        response: "ERROR_FETCHING_FIELDS",
      };
    }
  }
}
