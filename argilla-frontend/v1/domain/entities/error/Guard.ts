export class GuardError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "GuardError";

    // eslint-disable-next-line no-console
    console.error(`%cDevelop guard: ${message}`, "color:#F88989");
  }
}

export class Guard {
  private constructor() {}

  static condition(showThrow: boolean, message: string) {
    if (showThrow) {
      this.throw(message);
    }
  }

  static throw(message: string) {
    throw new GuardError(message);
  }
}
