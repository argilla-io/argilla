import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendField, Response } from "../types/";
import { Field } from "~/v1/domain/entities/Field";

export const enum FIELD_API_ERRORS {
  GET_QUESTIONS = "ERROR_FETCHING_FIELDS",
  UPDATE = "ERROR_PATCHING_FIELDS",
}

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
        response: FIELD_API_ERRORS.GET_QUESTIONS,
      };
    }
  }

  async update(field: Field): Promise<BackendField> {
    try {
      const { data } = await this.axios.patch<BackendField>(
        `/v1/fields/${field.id}`,
        this.createRequest(field)
      );

      return data;
    } catch (err) {
      throw {
        response: FIELD_API_ERRORS.UPDATE,
      };
    }
  }

  private createRequest({ title, settings }: Field): Partial<BackendField> {
    return {
      title,
      settings,
    };
  }
}
