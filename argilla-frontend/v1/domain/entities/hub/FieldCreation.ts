import { FieldType } from "../field/FieldType";

export class FieldCreation {
  public required = false;
  public readonly type: FieldType;
  constructor(public readonly name: string, type: string) {
    this.type = FieldType.from(type);
  }

  get title() {
    return this.name;
  }

  markAsRequired() {
    this.required = true;
  }
}
