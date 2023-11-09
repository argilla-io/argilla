export interface OptionForFilter {
  selected: boolean;
  label: string;
}

export interface RangeValue {
  ge?: number;
  le?: number;
}

export abstract class FilterWithOption {
  constructor(
    public readonly name: string,
    public readonly title: string,
    public readonly options: OptionForFilter[] = []
  ) {}

  public filterByText(text: string) {
    return this.options.filter((option) =>
      option.label.toLowerCase().includes(text.toLowerCase())
    );
  }

  public get selectedOptions(): OptionForFilter[] {
    return this.options.filter((option) => option.selected);
  }
}

export abstract class FilterWithScore {
  public value: RangeValue;
  constructor(
    public readonly name: string,
    public readonly title: string,
    public readonly min: number,
    public readonly max: number
  ) {
    this.value = {
      ge: min,
      le: max,
    };
  }
}
