export class Progress {
  constructor(
    public readonly total: number,
    public readonly submitted: number
  ) {}

  get remaining(): number {
    return this.total - this.submitted;
  }
}
