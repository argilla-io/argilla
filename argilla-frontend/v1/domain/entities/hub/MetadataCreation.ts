import { MetadataType } from "../metadata/MetadataType";

export const availableMetadataTypes = [
  MetadataType.from("int32"),
  MetadataType.from("int64"),
  MetadataType.from("float32"),
  MetadataType.from("float64"),
  MetadataType.from("terms"),
];

export type MetadataTypes = "int32" | "int64" | "float32" | "float64";

export class MetadataCreation {
  public readonly type: MetadataType;
  private constructor(
    public readonly name: string,
    type: string,
    public title?: string
  ) {
    this.title ??= this.name;
    this.type = MetadataType.from(type);
  }

  public static from(
    name: string,
    type: MetadataTypes | string
  ): MetadataCreation | null {
    if (availableMetadataTypes.map((t) => t.value).includes(type)) {
      return new MetadataCreation(name, type);
    }

    return null;
  }
}
