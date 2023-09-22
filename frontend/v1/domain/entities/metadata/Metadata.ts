class OptionForFilter {
  public selected = false;
  constructor(public readonly label: string) {}
}

export class Metadata {
  public value?: number; // TBD: For integer of float
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

  public get selectedOptions(): OptionForFilter[] {
    return this.options.filter((option) => option.selected);
  }

  public filterByText(text: string) {
    return this.options.filter((option) =>
      option.label.toLowerCase().includes(text.toLowerCase())
    );
  }

  public completeMetadata(value: string) {
    if (this.isTerms) {
      value.split(",").forEach((label) => {
        const option = this.options.find((option) => option.label === label);
        if (option) option.selected = true;
      });
    } else {
      this.value = Number(value);
    }
  }

  clear(): void {
    if (this.isTerms) return this.options.forEach((o) => (o.selected = false));

    this.value = null;
  }
}
