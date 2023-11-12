export abstract class Criteria {
  constructor() {
    this.reset();
  }

  abstract get isCompleted(): boolean;

  abstract get urlParams(): string;

  abstract complete(urlParams: string);

  abstract reset();
  isEqual(criteria: Criteria) {
    return this.urlParams === criteria.urlParams;
  }
}
