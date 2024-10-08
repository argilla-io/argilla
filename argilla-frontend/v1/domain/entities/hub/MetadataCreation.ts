export type MetadataTypes = "int32" | "int64" | "float32" | "float64";
export class MetadataCreation {
  public title: string;
  public constructor(
    public readonly name: string,
    public readonly type: MetadataTypes
  ) {
    this.title = this.name;
  }
}
