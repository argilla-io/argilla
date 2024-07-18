import { Progress } from "./Progress";

interface DatasetDistribution {
  strategy: string;
  minSubmitted: number;
}

interface OriginalDataset {
  guidelines: string;
  allowExtraMetadata: boolean;
  distribution: DatasetDistribution;
}

export class Dataset {
  public original: OriginalDataset;
  public progress: Progress;

  constructor(
    public readonly id: string,
    public readonly name: string,
    public guidelines: string,
    public readonly status: string,
    public readonly workspaceId: string,
    public readonly workspaceName: string,
    public allowExtraMetadata: boolean,
    public distribution: DatasetDistribution,
    public readonly createdAt: string,
    public updatedAt: string,
    public readonly lastActivityAt: string
  ) {
    this.initializeOriginal();
  }

  public get workspace() {
    return this.workspaceName;
  }

  public get isModified(): boolean {
    return (
      this.guidelines !== this.original.guidelines ||
      this.allowExtraMetadata !== this.original.allowExtraMetadata ||
      JSON.stringify(this.distribution) !==
        JSON.stringify(this.original.distribution)
    );
  }

  restore() {
    this.guidelines = this.original.guidelines;
    this.allowExtraMetadata = this.original.allowExtraMetadata;
    this.distribution = {
      ...this.original.distribution,
    };
  }

  update(when: string) {
    this.initializeOriginal();

    this.updatedAt = when;
  }

  private initializeOriginal() {
    this.original = {
      guidelines: this.guidelines,
      allowExtraMetadata: this.allowExtraMetadata,
      distribution: {
        ...this.distribution,
      },
    };
  }
}
