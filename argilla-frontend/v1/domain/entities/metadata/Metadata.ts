interface OriginalMetadata {
  title: string;
  visibleForAnnotators: boolean;
}

interface MetadataSettings {
  type: string;
  values?: string[];
  min?: number;
  max?: number;
}

export class Metadata {
  private original: OriginalMetadata;
  constructor(
    public readonly id: string,
    public name: string,
    public title: string,
    public settings: MetadataSettings,
    public visibleForAnnotators: boolean,
    public readonly datasetId: string
  ) {
    this.initializeOriginal();
  }

  public get isTerms() {
    return this.settings.type === "terms";
  }

  public get isInteger() {
    return this.settings.type === "integer";
  }

  public get isFloat() {
    return this.settings.type === "float";
  }

  get hasValues() {
    if (this.isTerms) return this.settings.values?.length > 0;

    return this.settings.max !== null && this.settings.min !== null;
  }

  public get isModified(): boolean {
    return (
      this.title.trim() !== this.original.title ||
      this.visibleForAnnotators !== this.original.visibleForAnnotators
    );
  }

  private MAX_TITLE_LENGTH = 500;
  public validate(): Record<"title", string[]> {
    const validations: Record<"title", string[]> = {
      title: [],
    };

    if (this.title?.length > this.MAX_TITLE_LENGTH)
      validations.title.push(
        `This must be less than ${this.MAX_TITLE_LENGTH}.`
      );

    return validations;
  }

  public get isValid(): boolean {
    return this.validate().title.length === 0;
  }

  restore() {
    this.title = this.original.title;
    this.visibleForAnnotators = this.original.visibleForAnnotators;
  }

  update(title: string, visibleForAnnotators: boolean) {
    this.title = title;
    this.visibleForAnnotators = visibleForAnnotators;

    this.initializeOriginal();
  }

  private initializeOriginal() {
    this.original = {
      title: this.title,
      visibleForAnnotators: this.visibleForAnnotators,
    };
  }
}
