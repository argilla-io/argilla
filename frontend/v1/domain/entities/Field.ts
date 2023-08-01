export class Field {
  public content: string;

  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly title: string,
    public readonly datasetId: string,
    public readonly required: boolean,
    public readonly settings: any
  ) {}

  public get isTextType() {
    return this.fieldType === "text";
  }

  public addContent(content: string) {
    this.content = content;
  }

  private get fieldType() {
    return this.settings?.type?.toLowerCase() ?? null;
  }
}
