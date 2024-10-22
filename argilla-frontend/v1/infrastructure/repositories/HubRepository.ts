import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { PublicNuxtAxiosInstance } from "../services";
import { DatasetCreation } from "~/v1/domain/entities/hub/DatasetCreation";

export class HubRepository {
  private axios: NuxtAxiosInstance;
  constructor(axios: PublicNuxtAxiosInstance) {
    this.axios = axios.makePublic({
      enableErrors: false,
    });
  }

  async getDatasetCreation(repoId: string): Promise<any> {
    try {
      const { data } = await this.axios.get(
        `https://datasets-server.huggingface.co/info?dataset=${encodeURIComponent(
          repoId
        )}`
      );

      return data.dataset_info;
    } catch {
      return {};
    }
  }

  async getFirstRecord(dataset: DatasetCreation): Promise<any> {
    try {
      const { repoId, selectedSubset } = dataset;
      const { data } = await this.axios.get(
        `https://datasets-server.huggingface.co/first-rows?dataset=${encodeURIComponent(
          repoId
        )}&split=${selectedSubset.selectedSplit.name}&config=${
          selectedSubset.name
        }`
      );

      return data.rows[0].row;
    } catch {
      return {};
    }
  }
}
