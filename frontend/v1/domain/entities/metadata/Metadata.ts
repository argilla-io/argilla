class OptionForFilter {
  public selected = false;
  constructor(public readonly label: string) {}
}
interface RangeValue {
  ge: number;
  le: number;
}

export class Metadata {
  public value: RangeValue;
  public options: OptionForFilter[];

  constructor(
    private id: string,
    public name: string,
    private description: string,
    public settings: any
  ) {
    if (this.isTerms) {
      this.options = this.settings.values.map((value: string) => {
        return new OptionForFilter(value);
      });
    } else {
      this.value = {
        ge: this.settings.min,
        le: this.settings.max,
      };
    }
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

  public get isAnswered(): boolean {
    return this.isTerms
      ? this.selectedOptions.length > 0
      : this.value.ge !== this.settings.min ||
          this.value.le !== this.settings.max;
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
      try {
        const { ge, le } = JSON.parse(value);
        this.value.ge = ge;
        this.value.le = le;
      } catch (error) {
        this.value.ge = this.settings.min;
        this.value.le = this.settings.max;
      }
    }
  }

  clear(): void {
    if (this.isTerms) return this.options.forEach((o) => (o.selected = false));

    this.value.ge = this.settings.min;
    this.value.le = this.settings.max;
  }
}
