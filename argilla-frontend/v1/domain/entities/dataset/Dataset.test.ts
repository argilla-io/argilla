import { createEmptyDataset } from "../__mocks__/dataset/mocks";

describe("Dataset", () => {
  describe("validate should", () => {
    test("return message when the guidelines is empty", () => {
      const dataset = createEmptyDataset();

      dataset.guidelines = "";

      expect(dataset.validate().guidelines).toEqual([
        "This field is required.",
      ]);
    });

    test("return a empty array when the guidelines is empty", () => {
      const dataset = createEmptyDataset();

      dataset.guidelines = "FAKE";

      expect(dataset.validate().guidelines).toHaveLength(0);
    });
  });
  describe("isValid should", () => {
    test("be false when the guidelines is empty", () => {
      const dataset = createEmptyDataset();

      dataset.guidelines = "";

      expect(dataset.isValid).toBeFalsy();
    });

    test("be true when the guidelines is empty", () => {
      const dataset = createEmptyDataset();

      dataset.guidelines = "FAKE";

      expect(dataset.isValid).toBeTruthy();
    });
  });
});
