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
    this.initializeOriginal();
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

  public get isFieldValid(): boolean {
    return this.validate().title.length === 0;
  }

  restore() {
    this.title = this.original.title;
    this.settings = {
      ...this.settings,
      ...this.original.settings,
    };
  }

  update(title: string, settings: any) {
    this.title = title;
    this.settings = settings;

    this.initializeOriginal();
  }

  private initializeOriginal() {
    this.original = {
      title: this.title,
      settings: {
        ...this.settings,
      },
    };
  }
}
