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

  get isModified(): boolean {
    return (
      this.isModifiedGuidelines ||
      this.isModifiedExtraMetadata ||
      this.isModifiedTaskDistribution
    );
  }

  get isModifiedGuidelines(): boolean {
    return this.guidelines !== this.original.guidelines;
  }

  get isModifiedExtraMetadata(): boolean {
    return this.allowExtraMetadata !== this.original.allowExtraMetadata;
  }

  get isModifiedTaskDistribution(): boolean {
    return (
      JSON.stringify(this.distribution) !==
      JSON.stringify(this.original.distribution)
    );
  }

  get isDraft(): boolean {
    return this.status === "draft";
  }

  restore(part: "guidelines" | "metadata" | "distribution") {
    if (part === "guidelines") return this.restoreGuidelines();

    if (part === "metadata") return this.restoreMetadata();

    if (part === "distribution") return this.restoreDistribution();
  }

  private restoreGuidelines() {
    this.guidelines = this.original.guidelines;
  }

  private restoreMetadata() {
    this.allowExtraMetadata = this.original.allowExtraMetadata;
  }

  private restoreDistribution() {
    this.distribution = {
      ...this.original.distribution,
    };
  }

  update(when: string, part: "guidelines" | "metadata" | "distribution") {
    this.original = {
      ...this.original,
    };

    if (part === "guidelines") {
      this.original.guidelines = this.guidelines;
    }

    if (part === "metadata") {
      this.original.allowExtraMetadata = this.allowExtraMetadata;
    }

    if (part === "distribution") {
      this.original.distribution = {
        ...this.distribution,
      };
    }

    this.updatedAt = when;
  }

  validate(): Record<"guidelines" | "distribution", string[]> {
    const validations: Record<"guidelines" | "distribution", string[]> = {
      guidelines: [],
      distribution: [],
    };

    if (this.guidelines?.trim().length < 1) {
      validations.guidelines.push("This field is required.");
    }

    if (!this.distribution.minSubmitted || this.distribution.minSubmitted < 1) {
      validations.distribution.push("This field is required.");
    }

    return validations;
  }

  get isValidGuidelines() {
    return this.validate().guidelines.length === 0;
  }

  get isValidDistribution() {
    return this.validate().distribution.length === 0;
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
