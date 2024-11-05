export class FieldType extends String {
  private constructor(value: string) {
    super(value);
  }

  public get value(): string {
    return this.toLowerCase();
  }

  public static from(value: string): FieldType {
    return new FieldType(value);
  }

  public get isTextType(): boolean {
    return this.value === "text";
  }

  public get isImageType(): boolean {
    return this.value === "image";
  }

  public get isChatType(): boolean {
    return this.value === "chat";
  }

  public get isCustomType(): boolean {
    return this.value === "custom";
  }
}
