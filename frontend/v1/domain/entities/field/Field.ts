interface OriginalField {
  title: string;
  settings: any;
}
export class Field {
  private original: OriginalField;
  constructor(
    public readonly id: string,
    public readonly name: string,
    public title: string,
    public readonly content: string,
    public readonly datasetId: string,
    public readonly required: boolean,
    public settings: any
  ) {
    this.original = {
      title,
      settings: { ...settings },
    };
  }

  public get isTextType() {
    return this.fieldType === "text";
  }

  private get fieldType() {
    return this.settings?.type?.toLowerCase() ?? null;
  }

  public get isModified(): boolean {
    return (
      this.title.trim() !== this.original.title ||
      this.settings.use_markdown !== this.original.settings.use_markdown
    );
  }

  restore() {
    this.title = this.original.title;
    this.settings = {
      ...this.settings,
      ...this.original.settings,
    };
  }
}
