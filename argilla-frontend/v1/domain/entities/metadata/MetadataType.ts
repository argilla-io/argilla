export class MetadataType extends String {
  private constructor(value: string) {
    super(value);
  }

  public get value(): string {
    return this.toLowerCase();
  }

  public static from(value: string): MetadataType {
    return new MetadataType(value);
  }

  public get isIntType(): boolean {
    return this.value === "int32" || this.value === "int64";
  }

  public get isFloatType(): boolean {
    return this.value === "float32" || this.value === "float64";
  }

  public get isTermsType(): boolean {
    return this.value === "terms";
  }
}
