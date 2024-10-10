import { FieldType } from "./FieldType";

interface OriginalField {
  title: string;
  settings: any;
}

export class Field {
  private original: OriginalField;
  public readonly content: string;

  public readonly sdkRecord?: unknown;

  constructor(
    public readonly id: string,
    public readonly name: string,
    public title: string,
    public readonly datasetId: string,
    public readonly isRequired: boolean,
    public settings: any,
    record?: any
  ) {
    this.initializeOriginal();

    if (this.isCustomType) {
      this.sdkRecord = record;
      this.content = settings.template;
    } else {
      this.content = record?.fields[name] ?? "";
    }
  }

  get isTextType() {
    return this.type.isTextType;
  }

  get isImageType() {
    return this.type.isImageType;
  }

  get isChatType() {
    return this.type === "chat";
  }

  get isCustomType() {
    return this.type === "custom";
  }

  private get type() {
    return FieldType.from(this.settings?.type);
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
