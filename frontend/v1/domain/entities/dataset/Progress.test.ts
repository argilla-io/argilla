import { Progress } from "./Progress";

describe("Progress", () => {
  test("should return the remaining number of submissions", () => {
    const progress = new Progress(10, 5);

    expect(progress.remaining).toBe(5);
  });

  test("should return 0 when there are no submissions", () => {
    const progress = new Progress(10, 2);

    expect(progress.submitted).toBe(2);
  });
});
