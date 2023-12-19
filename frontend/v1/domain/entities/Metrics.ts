export class Metrics {
  constructor(
    public readonly records: number,
    public readonly responses: number,
    public readonly submitted: number,
    public readonly discarded: number,
    public readonly draft: number
  ) {}

  public get total(): number {
    return this.records;
  }

  public get pending(): number {
    return this.records - this.responded;
  }

  public get pendingProgress(): number {
    return Math.round((this.pending / this.total) * 100 * 10) / 10;
  }

  public get draftProgress(): number {
    return Math.round((this.draft / this.total) * 100 * 10) / 10;
  }

  public get submittedProgress(): number {
    return Math.round((this.submitted / this.total) * 100 * 10) / 10;
  }

  public get discardedProgress(): number {
    return Math.round((this.discarded / this.total) * 100 * 10) / 10;
  }

  public get responded(): number {
    return this.submitted + this.draft + this.discarded;
  }

  public get respondedProgress(): number {
    return Math.round((this.responded / this.total) * 100 * 10) / 10;
  }
}
