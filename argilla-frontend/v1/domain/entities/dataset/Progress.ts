export class Progress {
  constructor(
    public readonly total: number,
    public readonly submitted: number,
    public readonly discarded: number,
    public readonly conflicting: number,
    public readonly pending: number
  ) {}
}
