import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Response } from "../types";
import { BackendEnvironment } from "../types/environment";
import { Environment } from "~/v1/domain/entities/environment/Environment";
import { IEnvironmentRepository } from "~/v1/domain/services/IEnvironmentRepository";

const enum ENVIRONMENT_API_ERRORS {
  FETCHING = "ERROR_FETCHING_ENVIRONMENT_SETTINGS",
}

export class EnvironmentRepository implements IEnvironmentRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getEnvironment(): Promise<Environment> {
    try {
      const { data } = await this.axios.get<Response<BackendEnvironment>>(
        "/v1/settings",
        { headers: { "cache-control": "max-age=240" } }
      );

      const { argilla, huggingface } = data.items;

      return new Environment(
        {
          showHuggingfaceSpacePersistantStorageWarning:
            argilla.show_huggingface_space_persistant_storage_warning,
        },
        {
          spaceId: huggingface.space_id,
          spaceTitle: huggingface.space_title,
          spaceSubdomain: huggingface.space_subdomain,
          spaceHost: huggingface.space_host,
          spaceRepoName: huggingface.space_repo_name,
          spaceAuthorName: huggingface.space_author_name,
          spacePersistantStorageEnabled:
            huggingface.space_persistant_storage_enabled,
        }
      );
    } catch (err) {
      throw {
        response: ENVIRONMENT_API_ERRORS.FETCHING,
      };
    }
  }
}
