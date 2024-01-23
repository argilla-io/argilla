import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { NuxtRuntimeConfig } from "@nuxt/types/config/runtime";
import { Response } from "../types";
import {
  OAuthProvider,
  ProviderType,
} from "~/v1/domain/entities/oauth/OAuthProvider";
import { IOAuthRepository } from "~/v1/domain/services/IOAuthRepository";
import { RouterService } from "~/v1/domain/services/RouterService";

const OAUTH_API_ERRORS = {
  ERROR_FETCHING_OAUTH_PROVIDERS: "ERROR_FETCHING_OAUTH_PROVIDERS",
  ERROR_FETCHING_OAUTH_ACCESS_TOKEN: "ERROR_FETCHING_OAUTH_ACCESS_TOKEN",
};

interface BackendOAuthProvider {
  name: "huggingface";
}

export class OAuthRepository implements IOAuthRepository {
  private readonly axios: NuxtAxiosInstance;
  constructor(
    axios: NuxtAxiosInstance,
    private readonly router: RouterService,
    private readonly config: NuxtRuntimeConfig
  ) {
    this.axios = axios.create({
      baseURL: "api/oauth2",
      withCredentials: false,
    });
  }

  async getProviders(): Promise<OAuthProvider[]> {
    try {
      const url = "providers";

      const { data } = await this.axios.get<Response<BackendOAuthProvider[]>>(
        url
      );

      return data.items.map((i) => new OAuthProvider(i.name));
    } catch {
      throw {
        response: OAUTH_API_ERRORS.ERROR_FETCHING_OAUTH_PROVIDERS,
      };
    }
  }

  authorize(provider: ProviderType) {
    this.router.go(
      `${this.config.backendURL}/oauth2/${provider}/authorize`,
      true
    );
  }

  async login(provider: string, params: string): Promise<string> {
    try {
      const url = `${provider}/access-token?${params}`;

      const { data } = await this.axios.get<{ access_token: string }>(url);

      return data.access_token;
    } catch {
      throw {
        response: OAUTH_API_ERRORS.ERROR_FETCHING_OAUTH_ACCESS_TOKEN,
      };
    }
  }
}
