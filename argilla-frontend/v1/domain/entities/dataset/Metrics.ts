export class Metrics {
  public readonly percentage: {
    pending: number;
    draft: number;
    submitted: number;
    discarded: number;
  };

  constructor(
    public readonly total: number,
    public readonly submitted: number,
    public readonly discarded: number,
    public readonly draft: number,
    public readonly pending: number
  ) {
    this.percentage = {
      pending: (this.pending * 100) / this.total,
      draft: (this.draft * 100) / this.total,
      submitted: (this.submitted * 100) / this.total,
      discarded: (this.discarded * 100) / this.total,
    };
  }

  get hasMetrics() {
    return this.total > 0;
  }

  get responded() {
    return this.submitted + this.discarded + this.draft;
  }

  get progress() {
    return this.responded / this.total;
  }
}
