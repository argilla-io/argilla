import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendField, Response } from "../types/";
import { mediumCache, revalidateCache } from "./AxiosCache";
import { Field } from "~/v1/domain/entities/field/Field";

export const enum FIELD_API_ERRORS {
  GET_QUESTIONS = "ERROR_FETCHING_FIELDS",
  UPDATE = "ERROR_PATCHING_FIELDS",
}

export class FieldRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getFields(datasetId: string): Promise<BackendField[]> {
    try {
      const { data } = await this.axios.get<Response<BackendField[]>>(
        `/v1/datasets/${datasetId}/fields`,
        mediumCache()
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

      revalidateCache(`/v1/datasets/${field.datasetId}/fields`);

      return data;
    } catch (err) {
      throw {
        response: FIELD_API_ERRORS.UPDATE,
      };
    }
  }

  private createRequest({
    name,
    title,
    settings,
  }: Field): Partial<BackendField> {
    return {
      title: !title || title === "" ? name : title,
      settings,
    };
  }
}
