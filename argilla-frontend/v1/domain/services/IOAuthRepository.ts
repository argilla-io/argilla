import {
  OAuthParams,
  OAuthProvider,
  ProviderType,
} from "../entities/oauth/OAuthProvider";

export interface IOAuthRepository {
  getProviders(): Promise<OAuthProvider[]>;

  authorize(provider: ProviderType): void;

  login(provider: ProviderType, oauthParams: OAuthParams): Promise<string>;
}
