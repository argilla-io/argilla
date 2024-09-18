import { Score } from "./Score";

describe("Score", () => {
  test("should get percentage with 1 decimal", () => {
    const score = new Score(0.123456789);

    expect(score.percentage).toEqual(12.3);
  });

  test("should get one hundred percentage", () => {
    const score = new Score(1);

    expect(score.percentage).toEqual(100);
  });

  test("should get zero percentage", () => {
    const score = new Score(0);

    expect(score.percentage).toEqual(0);
  });

  test("should be undefined when value is negative", () => {
    const score = new Score(-23.02);

    expect(score.percentage).toBeUndefined();
  });
});
