import { type NuxtAxiosInstance } from "@nuxtjs/axios";

export class HubRepository {
  constructor(private axios: NuxtAxiosInstance) {}

  // TODO: create return the type.
  async getDatasetCreation(repoId: string): Promise<any> {
    const { data } = await this.axios.get(
      `https://datasets-server.huggingface.co/info?dataset=${repoId}`
    );

    return data;
  }
}
