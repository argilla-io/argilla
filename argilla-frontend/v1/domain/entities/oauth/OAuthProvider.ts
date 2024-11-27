import { Dictionary } from "../common/Params";

export type ProviderType = "huggingface" | "keycloak" ;
export type OAuthParams = Dictionary<string | (string | null)[]>;
export class OAuthProvider {
  constructor(public readonly name: ProviderType) {}

  get isHuggingFace() {
    return this.name === "huggingface";
  }
  get isKeycloak() {
    return this.name === "keycloak";
  }
}
