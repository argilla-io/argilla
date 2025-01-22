export class Progress {
  public readonly percentage: {
    pending: string;
    completed: string;
  };

  public readonly hasMetrics: boolean;

  constructor(
    public readonly total: number,
    public readonly completed: number,
    public readonly pending: number,
    public readonly users: Array<{ username: string }>
  ) {
    this.hasMetrics = total >= 0;

    const percentagePending = (this.pending * 100) / this.total;
    const percentageCompleted = (this.completed * 100) / this.total;

    this.percentage = {
      pending: isNaN(percentagePending) ? "0.00" : percentagePending.toFixed(2),
      completed: isNaN(percentageCompleted)
        ? "0.00"
        : percentageCompleted.toFixed(2),
    };
  }

  get hasAtLeastTenRecord() {
    return this.total >= 10;
  }

  get isCompleted() {
    if (!this.hasMetrics) return false;
    if (this.total === 0) return false;

    return this.completed === this.total;
  }
}
