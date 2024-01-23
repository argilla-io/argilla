import { OAuthProvider, ProviderType } from "../entities/oauth/OAuthProvider";

export interface IOAuthRepository {
  getProviders(): Promise<OAuthProvider[]>;

  authorize(provider: ProviderType): void;
}
