class Debounce {
  private timer: NodeJS.Timeout;
  constructor(private readonly milliSeconds: number) {}

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
  const debounce = new Debounce(milliSeconds);

  return debounce;
};
