import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendVector } from "../types/vector";
import { Response } from "../types";
import { mediumCache, revalidateCache } from "./AxiosCache";
import { Vector } from "~/v1/domain/entities/vector/Vector";

const enum VECTOR_API_ERRORS {
  FETCHING = "ERROR_FETCHING_VECTORS",
  UPDATE = "ERROR_PATCHING_VECTORS",
}

export class VectorRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getVectors(datasetId: string): Promise<BackendVector[]> {
    try {
      const { data } = await this.axios.get<Response<BackendVector[]>>(
        `/v1/datasets/${datasetId}/vectors-settings`,
        mediumCache()
      );

      return data.items;
    } catch (err) {
      throw {
        response: VECTOR_API_ERRORS.FETCHING,
      };
    }
  }

  async update(vector: Vector): Promise<BackendVector> {
    try {
      const { data } = await this.axios.patch<BackendVector>(
        `/v1/vectors-settings/${vector.id}`,
        this.createRequest(vector)
      );

      revalidateCache(`/v1/datasets/${vector.datasetId}/vectors-settings`);

      return data;
    } catch (err) {
      throw {
        response: VECTOR_API_ERRORS.UPDATE,
      };
    }
  }

  private createRequest({ title }: Vector): Partial<BackendVector> {
    return {
      title,
    };
  }
}
