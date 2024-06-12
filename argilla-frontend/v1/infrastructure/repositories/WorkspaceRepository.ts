import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Response } from "../types";
import { mediumCache } from "./AxiosCache";

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
        mediumCache()
      );

      return data.items;
    } catch (err) {
      throw {
        response: WORKSPACES_API_ERRORS.GET_WORKSPACES,
      };
    }
  }
}
