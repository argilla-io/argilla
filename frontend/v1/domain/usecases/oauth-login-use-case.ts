import { ProviderType } from "../entities/oauth/OAuthProvider";
import { IOAuthRepository } from "../services/IOAuthRepository";

export class OAuthLoginUseCase {
  constructor(private readonly oauthRepository: IOAuthRepository) {}

  getProviders() {
    return this.oauthRepository.getProviders();
  }

  authorize(provider: ProviderType) {
    return this.oauthRepository.authorize(provider);
  }
}
