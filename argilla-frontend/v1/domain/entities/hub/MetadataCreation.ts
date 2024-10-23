import { MetadataType } from "../metadata/MetadataType";

export const availableMetadataTypes = [
  MetadataType.from("uint8"),
  MetadataType.from("uint16"),
  MetadataType.from("uint32"),
  MetadataType.from("uint64"),
  MetadataType.from("int8"),
  MetadataType.from("int32"),
  MetadataType.from("int64"),
  MetadataType.from("float16"),
  MetadataType.from("float32"),
  MetadataType.from("float64"),
  MetadataType.from("terms"),
];

const ADAPTED_TYPES = {
  uint8: "integer",
  uint16: "integer",
  uint32: "integer",
  uint64: "integer",
  int8: "integer",
  int32: "integer",
  int64: "integer",
  float16: "float",
  float32: "float",
  float64: "float",
};

export type MetadataTypes =
  | "uint8"
  | "uint16"
  | "uint32"
  | "unit64"
  | "int8"
  | "int32"
  | "int64"
  | "float32"
  | "float64";

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

  get adapteType() {
    return ADAPTED_TYPES[this.type.value];
  }
}
