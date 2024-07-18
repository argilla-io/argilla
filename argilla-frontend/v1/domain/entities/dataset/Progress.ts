export class Progress {
  public readonly percentage: {
    pending: string;
    completed: string;
  };

  constructor(
    public readonly total: number,
    public readonly completed: number,
    public readonly pending: number
  ) {
    this.percentage = {
      pending: ((this.pending * 100) / this.total).toFixed(2),
      completed: ((this.completed * 100) / this.total).toFixed(2),
    };
  }
}
