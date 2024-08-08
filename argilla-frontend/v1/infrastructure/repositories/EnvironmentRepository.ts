import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendEnvironment } from "../types/environment";
import { PublicNuxtAxiosInstance } from "../services/useAxiosExtension";
import { largeCache } from "./AxiosCache";
import { Environment } from "~/v1/domain/entities/environment/Environment";
import { IEnvironmentRepository } from "~/v1/domain/services/IEnvironmentRepository";

const enum ENVIRONMENT_API_ERRORS {
  FETCHING = "ERROR_FETCHING_ENVIRONMENT_SETTINGS",
}

export class EnvironmentRepository implements IEnvironmentRepository {
  private readonly axios: NuxtAxiosInstance;
  constructor(axios: PublicNuxtAxiosInstance) {
    this.axios = axios.makePublic();
  }

  async getEnvironment(): Promise<Environment> {
    try {
      const { data } = await this.axios.get<BackendEnvironment>(
        "v1/settings",
        largeCache()
      );

      const { argilla, huggingface } = data;

      return new Environment(
        {
          showHuggingfaceSpacePersistentStorageWarning:
            argilla.show_huggingface_space_persistent_storage_warning,
        },
        {
          spaceId: huggingface.space_id,
          spaceTitle: huggingface.space_title,
          spaceSubdomain: huggingface.space_subdomain,
          spaceHost: huggingface.space_host,
          spaceRepoName: huggingface.space_repo_name,
          spaceAuthorName: huggingface.space_author_name,
          spacePersistentStorageEnabled:
            huggingface.space_persistent_storage_enabled,
        }
      );
    } catch (err) {
      throw {
        response: ENVIRONMENT_API_ERRORS.FETCHING,
      };
    }
  }
}
