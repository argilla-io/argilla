class OptionForFilter {
  public selected = false;
  constructor(public readonly label: string) {}
}

export class Metadata {
  public options: OptionForFilter[];
  constructor(
    private id: string,
    public name: string,
    private description: string,
    private settings: any
  ) {
    this.options = this.settings.values?.map((value: string) => {
      return new OptionForFilter(value);
    });
  }

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
