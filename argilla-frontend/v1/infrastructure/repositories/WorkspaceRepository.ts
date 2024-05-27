import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Response } from "../types";

interface BackendWorkspace {
  id: string;
  name: string;
}

const enum WORKSPACES_API_ERRORS {
  GET_WORKSPACES = "GET_WORKSPACES",
}

export class WorkspaceRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}
  async getWorkspaces(): Promise<BackendWorkspace[]> {
    try {
      const { data } = await this.axios.get<Response<BackendWorkspace[]>>(
        "/v1/me/workspaces",
        { headers: { "cache-control": "max-age=120" } }
      );

      return data.items;
    } catch (err) {
      throw {
        response: WORKSPACES_API_ERRORS.GET_WORKSPACES,
      };
    }
  }
}
