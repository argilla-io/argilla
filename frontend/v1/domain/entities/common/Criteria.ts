import { RangeValue } from "./Filter";

export abstract class Criteria {
  constructor() {
    this.reset();
  }

  get isCompleted(): boolean {
    return true;
  }

  abstract get urlParams(): string;

  abstract complete(urlParams: string);

  abstract withValue(criteria: Criteria);

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
