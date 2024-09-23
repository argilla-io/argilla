import { Metrics } from "./Metrics";

describe("Metrics", () => {
  describe("hasMetrics", () => {
    it("should return true when there are records", () => {
      const metrics = new Metrics(1, 0, 0, 0, 0);

      const result = metrics.hasMetrics;

      expect(result).toBeTruthy();
    });
    it("should return false when there are no records", () => {
      const metrics = new Metrics(
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      );

      const result = metrics.hasMetrics;

      expect(result).toBeFalsy();
    });
  });

  describe("total", () => {
    it("should return the total number of records", () => {
      const metrics = new Metrics(15, 4, 5, 1, 5);

      const result = metrics.total;

      expect(result).toEqual(15);
    });
  });

  describe("responded", () => {
    it("should return the number of responded records", () => {
      const metrics = new Metrics(15, 4, 5, 1, 5);

      const result = metrics.responded;

      expect(result).toEqual(10);
    });
  });

  describe("pending", () => {
    it("should return the number of pending records", () => {
      const metrics = new Metrics(15, 4, 5, 1, 5);

      const result = metrics.pending;

      expect(result).toEqual(5);
    });
  });

  describe("progress", () => {
    it("should return the progress of responded records", () => {
      const metrics = new Metrics(15, 4, 5, 1, 5);

      const result = metrics.progress;

      expect(result).toEqual(0.6666666666666666);
    });
  });

  describe("percentage", () => {
    it("should return the percentage of draft records", () => {
      const metrics = new Metrics(15, 4, 5, 1, 5);

      const result = metrics.percentage.draft;

      expect(result).toEqual(6.666666666666667);
    });

    it("should return the percentage of submitted records", () => {
      const metrics = new Metrics(15, 4, 5, 1, 5);

      const result = metrics.percentage.submitted;

      expect(result).toEqual(26.666666666666668);
    });

    it("should return the percentage of discarded records", () => {
      const metrics = new Metrics(15, 4, 5, 1, 5);

      const result = metrics.percentage.discarded;

      expect(result).toEqual(33.333333333333336);
    });
  });
});
