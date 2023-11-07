interface OriginalDAtaset {
  guidelines: string;
  allowExtraMetadata: boolean;
}
export class Dataset {
  public original: OriginalDAtaset;
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly task: string,
    public guidelines: string,
    public readonly status: string,
    public readonly workspaceId: string,
    public readonly workspaceName: string,
    public readonly tags: unknown,
    public readonly createdAt: string,
    public updatedAt: string,
    public readonly lastActivityAt: string,
    public allowExtraMetadata: boolean
  ) {
    this.initializeOriginal();
  }

  public get workspace() {
    return this.workspaceName;
  }

  public get isModified(): boolean {
    return (
      this.guidelines !== this.original.guidelines ||
      this.allowExtraMetadata !== this.original.allowExtraMetadata
    );
  }

  restore() {
    this.guidelines = this.original.guidelines;
    this.allowExtraMetadata = this.original.allowExtraMetadata;
  }

  update(when: string) {
    this.initializeOriginal();

    this.updatedAt = when;
  }

  private initializeOriginal() {
    this.original = {
      guidelines: this.guidelines,
      allowExtraMetadata: this.allowExtraMetadata,
    };
  }
}
