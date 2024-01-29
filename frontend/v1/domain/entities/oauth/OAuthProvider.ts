export type ProviderType = "huggingface";

type Dictionary<T> = { [key: string]: T };
export type OAuthParams = Dictionary<string | (string | null)[]>;
export class OAuthProvider {
  constructor(public readonly name: ProviderType) {}

  get isHuggingFace() {
    return this.name === "huggingface";
  }
}
