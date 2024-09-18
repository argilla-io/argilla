export interface OptionForFilter {
  selected: boolean;
  value: string;
  text?: string;
}

export interface RangeValue {
  ge?: number;
  le?: number;
}

export type ValuesOption = {
  values: string[];
  operator?: "and" | "or";
};

export abstract class Filter {
  abstract get name(): string;

  abstract get value(): unknown;

  abstract complete(value: unknown): void;

  abstract clear(): void;

  abstract get isAnswered(): boolean;

  get canFilter() {
    return true;
  }
}

export class FilterWithOption extends Filter {
  constructor(
    public readonly name: string,
    public readonly options: OptionForFilter[] = []
  ) {
    super();
  }

  filterByText(text: string) {
    return this.options.filter((option) =>
      (option.text ?? option.value).toLowerCase().includes(text.toLowerCase())
    );
  }

  get selectedOptions(): OptionForFilter[] {
    return this.options.filter((option) => option.selected);
  }

  get isAnswered(): boolean {
    return this.selectedOptions.length > 0;
  }

  get value(): string[] {
    return this.selectedOptions.map((option) => option.value);
  }

  complete(value: string[]) {
    value.forEach((label) => {
      const option = this.options.find((option) => option.value === label);
      if (option) option.selected = true;
    });
  }

  clear(): void {
    return this.options.forEach((o) => (o.selected = false));
  }
}

export class FilterWithScore extends Filter {
  public rangeValue: RangeValue;
  constructor(
    public readonly name: string,
    public readonly min: number,
    public readonly max: number,
    public readonly isInteger = false
  ) {
    super();

    this.rangeValue = {
      ge: min,
      le: max,
    };
  }

  get settings() {
    return {
      min: this.min,
      max: this.max,
    };
  }

  get isAnswered(): boolean {
    return this.rangeValue.ge !== this.min || this.rangeValue.le !== this.max;
  }

  get value() {
    return {
      ge: this.rangeValue.ge,
      le: this.rangeValue.le,
    };
  }

  complete({ ge, le }: RangeValue) {
    this.rangeValue.ge = ge;
    this.rangeValue.le = le;
  }

  clear(): void {
    this.rangeValue.ge = this.min;
    this.rangeValue.le = this.max;
  }
}
