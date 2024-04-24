export class Environment {
  constructor(
    private readonly argilla: {
      showHuggingfaceSpacePersistantStorageWarning: boolean;
    },
    private readonly huggingface: {
      spaceId: string;
      spaceTitle: string;
      spaceSubdomain: string;
      spaceHost: string;
      spaceRepoName: string;
      spaceAuthorName: string;
      spacePersistantStorageEnabled: boolean;
    }
  ) {}

  get shouldShowHuggingfaceSpacePersistantStorageWarning(): boolean {
    return (
      this.argilla.showHuggingfaceSpacePersistantStorageWarning &&
      !this.huggingface.spacePersistantStorageEnabled
    );
  }
}
