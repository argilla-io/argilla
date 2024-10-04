import { FieldType } from "../field/FieldType";

export class FieldCreation {
  public required = false;
  public readonly type: FieldType;
  public title: string;
  constructor(public readonly name: string, type: "text" | "image" | "chat") {
    this.type = FieldType.from(type);
    this.title = this.name;
  }

  markAsRequired() {
    this.required = true;
  }
}
