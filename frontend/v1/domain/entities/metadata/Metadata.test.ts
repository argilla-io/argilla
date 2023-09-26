import { Metadata } from "./Metadata";

const createMetadataInteger = () =>
  new Metadata("1", "split", "The split of the record", {
    type: "integer",
    min: 0,
    max: 2,
  });
const createMetadataTerms = () =>
  new Metadata("1", "split", "The split of the record", {
    type: "terms",
    values: ["test", "train", "validation"],
  });
const createMetadataFloat = () =>
  new Metadata("1", "split", "The split of the record", {
    type: "float",
    min: 0.1,
    max: 3.76,
  });

describe("Metadata", () => {
  describe("Is terms", () => {
    test("should return true when the metadata is terms", () => {
      const metadata = createMetadataTerms();
      const isTerms = metadata.isTerms;
      expect(isTerms).toBe(true);
    });

    test("should return false when the metadata is not terms", () => {
      const metadata = createMetadataInteger();
      const isTerms = metadata.isTerms;
      expect(isTerms).toBe(false);
    });
  });
  describe("Is integer", () => {
    test("should return true when the metadata is integer", () => {
      const metadata = createMetadataInteger();
      const isInteger = metadata.isInteger;
      expect(isInteger).toBe(true);
    });

    test("should return false when the metadata is not integer", () => {
      const metadata = createMetadataTerms();
      const isInteger = metadata.isInteger;
      expect(isInteger).toBe(false);
    });
  });

  describe("Is float", () => {
    test("should return true when the metadata is float", () => {
      const metadata = createMetadataFloat();
      const isFloat = metadata.isFloat;
      expect(isFloat).toBe(true);
    });

    test("should return false when the metadata is not float", () => {
      const metadata = createMetadataTerms();
      const isFloat = metadata.isFloat;
      expect(isFloat).toBe(false);
    });
  });

  describe("Complete metadata", () => {
    test("should complete the metadata when is terms", () => {
      const metadata = createMetadataTerms();
      metadata.completeMetadata("test,train");
      expect(metadata.selectedOptions.map((option) => option.label)).toEqual([
        "test",
        "train",
      ]);
    });
    test("should complete the metadata when is integer", () => {
      const metadata = createMetadataInteger();
      metadata.completeMetadata(JSON.stringify({ ge: 10, le: 20 }));

      expect(metadata.value).toEqual({ ge: 10, le: 20 });
    });
  });

  describe("Clear", () => {
    test("should clear the metadata when is terms", () => {
      const metadata = createMetadataTerms();
      metadata.completeMetadata("test,train");
      metadata.clear();

      expect(metadata.selectedOptions.map((option) => option.label)).toEqual(
        []
      );
    });

    test("should clear the metadata when is integer set the settings max and min values", () => {
      const metadata = createMetadataInteger();
      metadata.completeMetadata(JSON.stringify({ ge: 10, le: 20 }));
      metadata.clear();

      expect(metadata.value).toEqual({ ge: 0, le: 2 });
    });
  });
});
