import {
  OAuthParams,
  OAuthProvider,
  ProviderType,
} from "../entities/oauth/OAuthProvider";
import { IOAuthRepository } from "../services/IOAuthRepository";

export class OAuthLoginUseCase {
  constructor(private readonly oauthRepository: IOAuthRepository) {}

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

  login(provider: ProviderType, oauthParams: OAuthParams) {
    return this.oauthRepository.login(provider, oauthParams);
  }
}
