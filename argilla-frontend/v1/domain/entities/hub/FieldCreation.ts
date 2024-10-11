import { FieldType } from "../field/FieldType";

export const noMapping = FieldType.from("no mapping");

export const availableFieldTypes = [
  noMapping,
  FieldType.from("text"),
  FieldType.from("image"),
  FieldType.from("chat"),
];

export type FieldCreationTypes = "no mapping" | "text" | "image" | "chat";

export class FieldCreation {
  public required = false;
  public type: FieldType;
  public dtype: string;
  public title: string;
  private constructor(
    public readonly name: string,
    type: string,
    dtype: string
  ) {
    this.type = FieldType.from(type);
    this.title = this.name;
    this.dtype = dtype;
  }

  markAsRequired() {
    this.required = true;
  }

  public static from(
    name: string,
    type: FieldCreationTypes,
    dtype: string
  ): FieldCreation | null {
    if (availableFieldTypes.map((t) => t.value).includes(type)) {
      return new FieldCreation(name, type, dtype);
    }

    return null;
  }
}
