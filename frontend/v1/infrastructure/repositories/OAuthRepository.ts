import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Auth } from "@nuxtjs/auth-next";
import { Response } from "../types";
import {
  OAuthProvider,
  ProviderType,
} from "~/v1/domain/entities/oauth/OAuthProvider";
import { IOAuthRepository } from "~/v1/domain/services/IOAuthRepository";

const OAUTH_API_ERRORS = {
  ERROR_FETCHING_OAUTH_PROVIDERS: "ERROR_FETCHING_OAUTH_PROVIDERS",
};

interface BackendOAuthProvider {
  name: "huggingface";
}

export class OAuthRepository implements IOAuthRepository {
  private readonly axios: NuxtAxiosInstance;
  constructor(axios: NuxtAxiosInstance, private readonly auth: Auth) {
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
    window.location.replace("http://0.0.0.0:6900/oauth2/huggingface/authorize");
  }
}
