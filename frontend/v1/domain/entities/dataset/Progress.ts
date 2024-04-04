export class Progress {
  constructor(
    public readonly total: number,
    public readonly submitted: number,
    public readonly conflicting: number,
    public readonly discarded: number
  ) {}

  get remaining(): number {
    return this.total - this.submitted;
  }
}
