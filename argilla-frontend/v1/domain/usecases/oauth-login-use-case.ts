import {
  OAuthParams,
  OAuthProvider,
  ProviderType,
} from "../entities/oauth/OAuthProvider";
import { IAuthService } from "../services/IAuthService";
import { IOAuthRepository } from "../services/IOAuthRepository";
import { LoadUserUseCase } from "./load-user-use-case";
import { RouterService } from "~/v1/domain/services/RouterService";

export class OAuthLoginUseCase {
  constructor(
    private readonly auth: IAuthService,
    private readonly oauthRepository: IOAuthRepository,
    private readonly loadUser: LoadUserUseCase,
    private readonly router: RouterService
  ) {}

  async getProviders(): Promise<OAuthProvider[]> {
    try {
      return await this.oauthRepository.getProviders();
    } catch {
      return Promise.resolve([]);
    }
  }

  authorize(provider: ProviderType) {
    return this.oauthRepository.authorize(provider);
  }

  redirect() {
    let { redirect } = this.router.getQuery();
    if (Array.isArray(redirect)) {
      redirect = redirect[0];
    }

    this.router.go(redirect || "/", {
      external: false,
      newWindow: false,
    });
  }

  async login(provider: ProviderType, oauthParams: OAuthParams) {
    await this.auth.logout();

    const token = await this.oauthRepository.login(provider, oauthParams);

    if (token) {
      await this.auth.setUserToken(token);

      await this.loadUser.execute();

      this.redirect();
    }
  }
}
