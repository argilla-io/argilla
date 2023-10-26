import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendVector } from "../types/vector";
import { Response } from "../types";
import { QUESTION_API_ERRORS } from "./QuestionRepository";

export const enum VECTOR_API_ERRORS {
  GET_VECTORS = "ERROR_FETCHING_VECTORS",
}

export class VectorRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getVectors(datasetId: string): Promise<BackendVector[]> {
    try {
      const { data } = await this.axios.get<Response<BackendVector[]>>(
        `/v1/datasets/${datasetId}/vectors-settings`
      );

      return data.items.map((v) => ({
        ...v,
        title: v.title ?? v.name, // TODO: Remove when we have titles for vectors
      }));
    } catch (err) {
      throw {
        response: QUESTION_API_ERRORS.GET_QUESTIONS,
      };
    }
  }
}
