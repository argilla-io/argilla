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
    private readonly record: any,
    public readonly datasetId: string,
    public readonly isRequired: boolean,
    public settings: any
  ) {
    this.initializeOriginal();
  }

  get isTextType() {
    return this.type === "text";
  }

  get isImageType() {
    return this.type === "image";
  }

  public get isChatType() {
    return this.type === "chat";
  }

  get isCustomType() {
    return this.fieldType === "custom";
  }

  get content() {
    if (this.isCustomType) {
      return `<script>const record_object = ${JSON.stringify(
        this.record
      )};</script>
      ${this.settings.template}`;
    }

    return this.record.fields[this.name];
  }

  private get type() {
    return this.settings?.type?.toLowerCase() ?? null;
  }

  get isModified(): boolean {
    return (
      this.title.trim() !== this.original.title ||
      this.settings.use_markdown !== this.original.settings.use_markdown
    );
  }

  private MAX_TITLE_LENGTH = 500;
  validate(): Record<"title", string[]> {
    const validations: Record<"title", string[]> = {
      title: [],
    };

    if (this.title?.length > this.MAX_TITLE_LENGTH)
      validations.title.push(
        `This must be less than ${this.MAX_TITLE_LENGTH}.`
      );

    return validations;
  }

  get isFieldValid(): boolean {
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
