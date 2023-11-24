export interface OptionForFilter {
  selected: boolean;
  label: string;
}

export interface RangeValue {
  ge?: number;
  le?: number;
}

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
      option.label.toLowerCase().includes(text.toLowerCase())
    );
  }

  get selectedOptions(): OptionForFilter[] {
    return this.options.filter((option) => option.selected);
  }

  get isAnswered(): boolean {
    return this.selectedOptions.length > 0;
  }

  get value(): string[] {
    return this.selectedOptions.map((option) => option.label);
  }

  complete(value: string[]) {
    value.forEach((label) => {
      const option = this.options.find((option) => option.label === label);
      if (option) option.selected = true;
    });
  }

  clear(): void {
    return this.options.forEach((o) => (o.selected = false));
  }
}

export class FilterWithScore extends Filter {
  public value: RangeValue;
  constructor(
    public readonly name: string,
    public readonly min: number,
    public readonly max: number,
    public readonly isInteger = false
  ) {
    super();

    this.value = {
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
    return this.value.ge !== this.min || this.value.le !== this.max;
  }

  get values() {
    return this.value;
  }

  complete({ ge, le }: RangeValue) {
    this.value.ge = ge;
    this.value.le = le;
  }

  clear(): void {
    this.value.ge = this.min;
    this.value.le = this.max;
  }
}
