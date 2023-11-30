import { RangeValue } from "./Filter";

export abstract class Criteria {
  constructor() {
    this.reset();
  }

  abstract get isCompleted(): boolean;

  abstract get urlParams(): string;

  abstract complete(urlParams: string);

  abstract reset();

  protected getRangeValue(value: string): RangeValue {
    const regex = /ge(-?\d+(\.\d+)?)\.le(-?\d+(\.\d+)?)/;
    const score = value.match(regex);

    if (score) {
      return {
        ge: Number(score[1]),
        le: Number(score[3]),
      };
    }
  }

  isEqual(criteria: Criteria) {
    return this.urlParams === criteria.urlParams;
  }
}
