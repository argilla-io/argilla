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

  private constructor(public readonly name: string, type: string) {
    this.title = this.name;

    this.settings = {
      type: FieldType.from(type),
    };
  }

  get type(): FieldType {
    return this.settings.type;
  }

  markAsRequired() {
    this.required = true;
  }

  public static from(
    name: string,
    type: FieldCreationTypes
  ): FieldCreation | null {
    if (availableFieldTypes.map((t) => t.value).includes(type)) {
      return new FieldCreation(name, type);
    }

    return null;
  }
}
