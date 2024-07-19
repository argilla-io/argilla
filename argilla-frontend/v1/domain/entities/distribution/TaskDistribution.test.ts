import { TaskDistribution } from "./TaskDistribution";

describe("Task Distribution should", () => {
  describe("isCompleted", () => {
    test("should be true if the status is 'completed", () => {
      const taskDistribution = new TaskDistribution("completed");

      expect(taskDistribution.isCompleted).toBeTruthy();
    });

    test("should be false if the status is 'completed", () => {
      const taskDistribution = new TaskDistribution("pending");

      expect(taskDistribution.isCompleted).toBeFalsy();
    });
  });
});
