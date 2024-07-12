export class Progress {
  constructor(
    public readonly total: number,
    public readonly completed: number,
    public readonly pending: number
  ) {}
}
