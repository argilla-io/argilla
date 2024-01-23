export type ProviderType = "huggingface";

export class OAuthProvider {
  constructor(public readonly name: ProviderType) {}

  get isHuggingFace() {
    return this.name === "huggingface";
  }
}
