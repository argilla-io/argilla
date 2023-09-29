export class Metadata {
  constructor(
    private id: string,
    public name: string,
    private description: string,
    public settings: any
  ) {}

  public get isTerms() {
    return this.settings.type === "terms";
  }

  public get isInteger() {
    return this.settings.type === "integer";
  }

  public get isFloat() {
    return this.settings.type === "float";
  }
}
