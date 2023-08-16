export class Field {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly content: string,
    public readonly datasetId: string,
    public readonly required: boolean,
    public readonly settings: any
  ) {}

  public get isTextType() {
    return this.fieldType === "text";
  }

  private get fieldType() {
    return this.settings?.type?.toLowerCase() ?? null;
  }
}
