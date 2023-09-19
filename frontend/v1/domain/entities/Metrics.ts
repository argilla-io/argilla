export class Metrics {
  constructor(
    public readonly records: number,
    public readonly responses: number,
    public readonly submitted: number,
    public readonly discarded: number
  ) {}
}
