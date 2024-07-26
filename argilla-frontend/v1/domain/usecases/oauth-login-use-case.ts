import {
  OAuthParams,
  OAuthProvider,
  ProviderType,
} from "../entities/oauth/OAuthProvider";
import { IAuthService } from "../services/IAuthService";
import { IOAuthRepository } from "../services/IOAuthRepository";

export class OAuthLoginUseCase {
  constructor(
    private readonly oauthRepository: IOAuthRepository,
    private readonly auth: IAuthService
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

    if (token) this.auth.setUserToken(token);
  }
}
