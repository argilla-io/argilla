import { Metrics } from "./Metrics";

describe("Metrics", () => {
  describe("hasMetrics", () => {
    it("should return true when there are records", () => {
      const metrics = new Metrics(1, 0, 0, 0, 0);

      const result = metrics.hasMetrics;

      expect(result).toBeTruthy();
    });
    it("should return false when there are no records", () => {
      const metrics = new Metrics(0, 0, 0, 0, 0);

      const result = metrics.hasMetrics;

      expect(result).toBeFalsy();
    });
  });

  describe("total", () => {
    it("should return the total number of records", () => {
      const metrics = new Metrics(1, 0, 0, 0, 0);

      const result = metrics.total;

      expect(result).toEqual(1);
    });
  });

  describe("responded", () => {
    it("should return the number of responded records", () => {
      const metrics = new Metrics(5, 5, 3, 1, 1);

      const result = metrics.responded;

      expect(result).toEqual(5);
    });
  });

  describe("pending", () => {
    it("should return the number of pending records", () => {
      const metrics = new Metrics(5, 4, 3, 1, 0);

      const result = metrics.pending;

      expect(result).toEqual(1);
    });
  });

  describe("progress", () => {
    it("should return the progress of responded records", () => {
      const metrics = new Metrics(5, 4, 3, 1, 0);

      const result = metrics.progress;

      expect(result).toEqual(0.8);
    });
  });

  describe("percentage", () => {
    it("should return the percentage of draft records", () => {
      const metrics = new Metrics(5, 4, 3, 1, 1);

      const result = metrics.percentage.draft;

      expect(result).toEqual(20);
    });

    it("should return the percentage of submitted records", () => {
      const metrics = new Metrics(5, 4, 3, 1, 1);

      const result = metrics.percentage.submitted;

      expect(result).toEqual(60);
    });

    it("should return the percentage of discarded records", () => {
      const metrics = new Metrics(5, 4, 3, 1, 1);

      const result = metrics.percentage.discarded;

      expect(result).toEqual(20);
    });
  });
});
