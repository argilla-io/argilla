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

  describe("isValidGuidelines should", () => {
    test("be false when the guidelines is empty", () => {
      const dataset = createEmptyDataset();

      dataset.guidelines = "";

      expect(dataset.isValidGuidelines).toBeFalsy();
    });

    test("be true when the guidelines is empty", () => {
      const dataset = createEmptyDataset();

      dataset.guidelines = "FAKE";

      expect(dataset.isValidGuidelines).toBeTruthy();
    });
  });

  describe("isValidDistribution should", () => {
    test("be false when the min submitted is empty", () => {
      const dataset = createEmptyDataset();

      dataset.distribution.minSubmitted = undefined;

      expect(dataset.isValidDistribution).toBeFalsy();
    });

    test("be true when the min submitted is lower than 0", () => {
      const dataset = createEmptyDataset();

      dataset.distribution.minSubmitted = -1;

      expect(dataset.isValidDistribution).toBeFalsy();
    });

    test("be true when the min submitted is lower than 0", () => {
      const dataset = createEmptyDataset();

      dataset.distribution.minSubmitted = 20;

      expect(dataset.isValidDistribution).toBeTruthy();
    });
  });

  describe("restore", () => {
    test("restore only the distribution based on original values", () => {
      const dataset = createEmptyDataset();
      dataset.distribution.minSubmitted = 20;

      expect(dataset.distribution).not.toEqual(dataset.original.distribution);

      dataset.restore("distribution");

      expect(dataset.distribution).toEqual(dataset.original.distribution);
    });

    test("restore only the metadata info based on original values", () => {
      const dataset = createEmptyDataset();
      dataset.allowExtraMetadata = true;

      expect(dataset.allowExtraMetadata).not.toEqual(
        dataset.original.allowExtraMetadata
      );

      dataset.restore("metadata");

      expect(dataset.allowExtraMetadata).toEqual(
        dataset.original.allowExtraMetadata
      );
    });

    test("restore only the guidelines based on original values", () => {
      const dataset = createEmptyDataset();
      dataset.guidelines = "NEW GUIDELINES";

      expect(dataset.guidelines).not.toEqual(dataset.original.guidelines);

      dataset.restore("guidelines");

      expect(dataset.guidelines).toEqual(dataset.original.guidelines);
    });
  });

  describe("update should", () => {
    test("update just the guidelines", () => {
      const dataset = createEmptyDataset();
      dataset.guidelines = "NEW GUIDELINES";

      expect(dataset.guidelines).not.toEqual(dataset.original.guidelines);

      dataset.update("TODAY", "guidelines");

      expect(dataset.guidelines).toEqual(dataset.original.guidelines);
      expect(dataset.distribution.minSubmitted).toBe(
        dataset.original.distribution.minSubmitted
      );
      expect(dataset.allowExtraMetadata).toBe(
        dataset.original.allowExtraMetadata
      );
    });

    test("update just the task distribution", () => {
      const dataset = createEmptyDataset();
      dataset.distribution.minSubmitted = 20;

      expect(dataset.distribution.minSubmitted).not.toEqual(
        dataset.original.distribution.minSubmitted
      );

      dataset.update("TODAY", "distribution");

      expect(dataset.distribution.minSubmitted).toEqual(
        dataset.original.distribution.minSubmitted
      );
      expect(dataset.guidelines).toBe(dataset.original.guidelines);
      expect(dataset.allowExtraMetadata).toBe(
        dataset.original.allowExtraMetadata
      );
    });

    test("update just the metadata", () => {
      const dataset = createEmptyDataset();
      dataset.allowExtraMetadata = true;

      expect(dataset.allowExtraMetadata).not.toEqual(
        dataset.original.allowExtraMetadata
      );

      dataset.update("TODAY", "metadata");

      expect(dataset.allowExtraMetadata).toEqual(
        dataset.original.allowExtraMetadata
      );
      expect(dataset.guidelines).toBe(dataset.original.guidelines);
      expect(dataset.distribution.minSubmitted).toBe(
        dataset.original.distribution.minSubmitted
      );
    });
  });
});
