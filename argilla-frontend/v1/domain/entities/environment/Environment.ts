export class Environment {
  constructor(
    private readonly argilla: {
      showHuggingfaceSpacePersistentStorageWarning: boolean;
    },
    private readonly huggingface: {
      spaceId: string;
      spaceTitle: string;
      spaceSubdomain: string;
      spaceHost: string;
      spaceRepoName: string;
      spaceAuthorName: string;
      spacePersistentStorageEnabled: boolean;
    }
  ) {}

  get shouldShowHuggingfaceSpacePersistentStorageWarning(): boolean {
    return (
      this.argilla.showHuggingfaceSpacePersistentStorageWarning &&
      !this.huggingface.spacePersistentStorageEnabled
    );
  }

  get huggingFaceSpace() {
    if (this.huggingface?.spaceId) {
      return {
        space: this.huggingface.spaceRepoName,
        user: this.huggingface.spaceAuthorName,
        host: this.huggingface.spaceHost,
      };
    }
  }
}
