export class Metrics {
  public readonly percentage: {
    draft: number;
    submitted: number;
    discarded: number;
  };

  constructor(
    private readonly records: number,
    public readonly responses: number,
    public readonly submitted: number,
    public readonly discarded: number,
    public readonly draft: number
  ) {
    this.percentage = {
      draft: (this.draft * 100) / this.total,
      submitted: (this.submitted * 100) / this.total,
      discarded: (this.discarded * 100) / this.total,
    };
  }

  get hasMetrics() {
    return this.records > 0;
  }

  get total() {
    return this.records;
  }

  get responded() {
    return this.submitted + this.discarded + this.draft;
  }

  get pending() {
    return this.total - this.responded;
  }

  get progress() {
    return this.responded / this.total;
  }
}
