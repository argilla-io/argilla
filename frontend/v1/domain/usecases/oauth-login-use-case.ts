import { ProviderType } from "../entities/oauth/OAuthProvider";
import { AuthenticationService } from "../services/AuthenticationService";
import { IOAuthRepository } from "../services/IOAuthRepository";

export class OAuthLoginUseCase {
  constructor(
    private readonly oauthRepository: IOAuthRepository,
    private readonly auth: AuthenticationService
  ) {}

  getProviders() {
    return this.oauthRepository.getProviders();
  }

  authorize(provider: ProviderType) {
    return this.oauthRepository.authorize(provider);
  }

  async login(provider: ProviderType, code: string) {
    const token = await this.oauthRepository.login(provider, code);

    await this.auth.setUserToken(token);
  }
}
