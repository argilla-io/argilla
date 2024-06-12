import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Auth } from "@nuxtjs/auth-next";
import { Response } from "../types";
import { useRunningEnvironment } from "../services/useRunningEnvironment";
import { largeCache } from "./AxiosCache";
import {
  OAuthParams,
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
    private readonly auth: Auth
  ) {
    this.axios = axios.create({
      withCredentials: false,
    });
  }

  async getProviders(): Promise<OAuthProvider[]> {
    try {
      const url = "v1/oauth2/providers";

      const { data } = await this.axios.get<Response<BackendOAuthProvider[]>>(
        url,
        largeCache()
      );

      return data.items.map((i) => new OAuthProvider(i.name));
    } catch {
      throw {
        response: OAUTH_API_ERRORS.ERROR_FETCHING_OAUTH_PROVIDERS,
      };
    }
  }

  authorize(provider: ProviderType) {
    const { isEmbebed } = useRunningEnvironment();

    const oauthParams = this.router.getQuery();
    const params = this.createParams(oauthParams);
    let urlToRedirect = `api/v1/oauth2/providers/${provider}/authentication`;

    if (params.size) urlToRedirect += `?${params.toString()}`;

    this.router.go(urlToRedirect, {
      external: true,
      newWindow: isEmbebed(),
    });
  }

  async login(provider: ProviderType, oauthParams: OAuthParams) {
    try {
      const url = `v1/oauth2/providers/${provider}/access-token`;

      const params = this.createParams(oauthParams);

      const { data } = await this.axios.get<{ access_token: string }>(url, {
        params,
      });

      if (data.access_token) await this.auth.setUserToken(data.access_token);
    } catch (error) {
      throw {
        response: OAUTH_API_ERRORS.ERROR_FETCHING_OAUTH_ACCESS_TOKEN,
      };
    }
  }

  private createParams(oauthParams: OAuthParams) {
    const params = new URLSearchParams();

    Object.entries(oauthParams).forEach(([key, value]) => {
      params.append(key, value.toString());
    });

    return params;
  }
}
