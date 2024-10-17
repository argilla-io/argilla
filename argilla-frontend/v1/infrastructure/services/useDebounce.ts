export class Debounce {
  private timer: NodeJS.Timeout;
  private constructor(private readonly milliSeconds: number) {}

  static from(milliSeconds: number) {
    return new Debounce(milliSeconds);
  }

  wait() {
    this.stop();

    return new Promise<void>((resolve) => {
      this.timer = setTimeout(() => {
        resolve();
        this.timer = null;
      }, this.milliSeconds);
    });
  }

  stop() {
    if (this.timer) {
      clearTimeout(this.timer);
    }
  }
}

export const useDebounce = (milliSeconds: number) => {
  const debounce = Debounce.from(milliSeconds);

  return debounce;
};
