/* eslint-disable camelcase */
import { type NuxtAxiosInstance } from "@nuxtjs/axios";

export class HubRepository {
  constructor(private axios: NuxtAxiosInstance) {}

  async getDatasetCreation(repoId: string): Promise<any> {
    try {
      const { data } = await this.axios.get(
        `https://datasets-server.huggingface.co/info?dataset=${encodeURIComponent(
          repoId
        )}`
      );

      const { dataset_info } = data;

      if ("datasets" in dataset_info) return dataset_info.datasets;

      return dataset_info;
    } catch {
      return {};
    }
  }

  async getFirstRecord(repoId: string, split: string): Promise<any> {
    try {
      const { data } = await this.axios.get(
        `https://datasets-server.huggingface.co/first-rows?dataset=${encodeURIComponent(
          repoId
        )}&split=${split}&config=default`
      );

      return data;
    } catch {
      return {};
    }
  }
}
