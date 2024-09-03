import {
  OAuthParams,
  OAuthProvider,
  ProviderType,
} from "../entities/oauth/OAuthProvider";
import { IAuthService } from "../services/IAuthService";
import { IOAuthRepository } from "../services/IOAuthRepository";
import { LoadUserUseCase } from "./load-user-use-case";

export class OAuthLoginUseCase {
  constructor(
    private readonly auth: IAuthService,
    private readonly oauthRepository: IOAuthRepository,
    private readonly loadUser: LoadUserUseCase
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

  async login(provider: ProviderType, oauthParams: OAuthParams) {
    await this.auth.logout();

    const token = await this.oauthRepository.login(provider, oauthParams);

    if (token) {
      await this.auth.setUserToken(token);

      await this.loadUser.execute();
    }
  }
}
