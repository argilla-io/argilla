import { User } from "../user/User";
import { Progress } from "./Progress";

interface DatasetDistribution {
  strategy: string;
  minSubmitted: number;
}

interface DatasetMetadata {
  repoId: string;
  subset: string;
  split: string;
  mapping: {
    fields: { source: string; target: string }[];
    metadata: { source: string; target: string }[];
    suggestions: { source: string; target: string }[];
    external_id?: string;
  };
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
    public readonly metadata: DatasetMetadata,
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

  get createdFromUI() {
    return !!this.metadata?.repoId;
  }

  createCodeSnippetFromHub(user: User) {
    if (!this.createdFromUI) return;

    const mappingArg = {};

    for (const suggestion of this.metadata.mapping.suggestions) {
      mappingArg[suggestion.source] = `${suggestion.target}.suggestion`;
    }

    const { repoId, subset, split } = this.metadata;

    const snippet = `
  \`\`\`python
  import argilla as rg
  from datasets import load_dataset

  client = rg.Argilla(
    api_url="${window.location.origin}",
    api_key="${user.apiKey}"
  )

  ds = load_dataset("${repoId}", name="${subset}", split="${split}")

  dataset = client.datasets(name="${this.name}", workspace="${
      this.workspaceName
    }")

  dataset.records.log(ds, mapping=${JSON.stringify(mappingArg)})
  \`\`\``;

    return snippet;
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
