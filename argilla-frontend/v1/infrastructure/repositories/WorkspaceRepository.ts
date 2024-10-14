import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Response } from "../types";
import { mediumCache, revalidateCache } from "./AxiosCache";

interface BackendWorkspace {
  id: string;
  name: string;
}

const enum WORKSPACES_API_ERRORS {
  GET_WORKSPACES = "GET_WORKSPACES",
  CREATE_WORKSPACE = "CREATE_WORKSPACE",
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

  async create(name: string): Promise<BackendWorkspace> {
    try {
      const { data } = await this.axios.post<BackendWorkspace>(
        "/v1/workspaces",
        {
          name,
        }
      );

      revalidateCache("/v1/me/workspaces");

      return data;
    } catch (err) {
      throw {
        response: WORKSPACES_API_ERRORS.CREATE_WORKSPACE,
      };
    }
  }
}
