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
  public title: string;
  public readonly settings: { type: FieldType };

  public readonly originalType: FieldType;

  private constructor(
    public readonly name: string,
    type: string,
    public readonly primitiveType: string
  ) {
    this.title = this.name;

    this.settings = {
      type: FieldType.from(type),
    };

    this.originalType = FieldType.from(type);
  }

  get type(): FieldType {
    return this.settings.type;
  }

  set type(value: FieldType) {
    this.settings.type = value;
  }

  get isTextType() {
    return this.type.isTextType;
  }

  get isImageType() {
    return this.type.isImageType;
  }

  get isChatType() {
    return this.type.isChatType;
  }

  get isCustomType() {
    return this.type.isCustomType;
  }

  markAsRequired() {
    this.required = true;
  }

  public static from(
    name: string,
    type: FieldCreationTypes,
    primitiveType: string
  ): FieldCreation | null {
    if (availableFieldTypes.map((t) => t.value).includes(type)) {
      return new FieldCreation(name, type, primitiveType);
    }

    return null;
  }
}
