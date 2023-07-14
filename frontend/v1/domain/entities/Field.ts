export class Field {
  public readonly component_type: string;
  public readonly dataset_id: string;
  public readonly is_required: boolean;

  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly content: string,
    public readonly datasetId: string,
    public readonly required: boolean,
    public readonly settings: any
  ) {
    this.dataset_id = this.datasetId;
    this.is_required = this.required;
  }

  public get isTextType() {
    return this.fieldType === "text";
  }

  private get fieldType() {
    return this.settings?.type?.toLowerCase() ?? null;
  }
}
