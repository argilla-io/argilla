export class Score {
  constructor(public readonly value: number) {}

  get percentage(): number {
    if (this.value < 0) return undefined;

    return Math.round(this.value * 100 * 10) / 10;
  }
}
