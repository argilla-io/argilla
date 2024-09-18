import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Response } from "../types";
import { mediumCache } from "./AxiosCache";

interface BackendAgent {
  question: {
    id: string;
    name: string;
  };

  agents: string[];
}

const enum AGENTS_API_ERRORS {
  GET_AGENTS = "GET_AGENTS",
}

export class AgentRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}
  async getAgents(datasetId: string): Promise<BackendAgent[]> {
    try {
      const { data } = await this.axios.get<Response<BackendAgent[]>>(
        `/v1/datasets/${datasetId}/records/search/suggestions/options`,
        mediumCache()
      );

      return data.items;
    } catch (err) {
      throw {
        response: AGENTS_API_ERRORS.GET_AGENTS,
      };
    }
  }
}
