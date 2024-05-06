import { createVectorMock } from "../__mocks__/vector/mocks";
import { Metadata } from "./Metadata";

const createMetadataInteger = () =>
  new Metadata(
    "1",
    "split",
    "The split of the record",
    {
      type: "integer",
      min: 0,
      max: 2,
    },
    true,
    "FAKE_DATASET_ID"
  );
const createMetadataTerms = () =>
  new Metadata(
    "1",
    "split",
    "The split of the record",
    {
      type: "terms",
      values: ["test", "train", "validation"],
    },
    true,
    "FAKE_DATASET_ID"
  );
const createMetadataFloat = () =>
  new Metadata(
    "1",
    "split",
    "The split of the record",
    {
      type: "float",
      min: 0.1,
      max: 3.76,
    },
    true,
    "FAKE_DATASET_ID"
  );

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

  describe("restore should", () => {
    test("can restore previous title", () => {
      const metadata = createMetadataTerms();
      const originalTitle = metadata.title;
      metadata.title = "NEW TITLE";

      metadata.restore();

      expect(metadata.title).toBe(originalTitle);
    });
  });

  describe("isModified should", () => {
    test("true when title does not match with original", () => {
      const metadata = createMetadataTerms();
      metadata.title = "NEW TITLE";

      expect(metadata.isModified).toBeTruthy();
    });

    test("false when title does not match with original", () => {
      const metadata = createMetadataTerms();
      metadata.title += "       ";

      expect(metadata.isModified).toBeFalsy();
    });

    test("true when visibleForAnnotators does not match with original", () => {
      const metadata = createMetadataTerms();
      metadata.visibleForAnnotators = !metadata.visibleForAnnotators;

      expect(metadata.isModified).toBeTruthy();
    });
  });

  describe("update should", () => {
    test("isModified is false when the metadata was updated", () => {
      const FAKE_TITLE_FROM_BACKEND = "TITLE FROM BACKEND";
      const metadata = createMetadataTerms();
      metadata.title = "NEW TITLE";

      expect(metadata.isModified).toBeTruthy();

      metadata.update(FAKE_TITLE_FROM_BACKEND, metadata.visibleForAnnotators);

      expect(metadata.isModified).toBeFalsy();
      expect(metadata.title).toBe(FAKE_TITLE_FROM_BACKEND);
    });

    test("isModified is false when the metadata visible for annotator was updated", () => {
      const metadata = createMetadataTerms();
      metadata.visibleForAnnotators = false;

      expect(metadata.isModified).toBeTruthy();

      metadata.update(metadata.title, false);

      expect(metadata.isModified).toBeFalsy();
      expect(metadata.visibleForAnnotators).toBeFalsy();
    });
  });

  describe("metadata validation should", () => {
    const invalidLargeTitle =
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum rhoncus mauris sit amet turpis euismod lobortis. Donec sit amet justo non tellus viverra pharetra. Vestibulum vitae aliquet dui. Etiam nec diam cursus, aliquam ligula vitae, volutpat lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Sed et placerat enim. Aenean ut ante dapibus enim tincidunt tempor sed sit amet velit. Quisque vehicula risus quis velit blandit auctor. Maecenas eget accumsan erat.";

    describe("validate should", () => {
      test("return 'This must be less than 500.' error if metadata title has more 500 characters", () => {
        const metadata = createVectorMock("1");
        metadata.title = invalidLargeTitle;
        expect(metadata.validate().title).toStrictEqual([
          "This must be less than 500.",
        ]);
      });
      test("don't return error if metadata has a valid title", () => {
        const metadata = createVectorMock("1");
        metadata.title = "TITLE";
        expect(metadata.validate().title).toStrictEqual([]);
      });
    });

    describe("is valid", () => {
      test("return true when title is valid", () => {
        const metadata = createVectorMock("1");
        metadata.title = "TITLE";
        expect(metadata.isValid).toBeTruthy();
      });
      test("return false when title is invalid or description is invalid", () => {
        const metadata = createVectorMock("1");
        metadata.title = invalidLargeTitle;
        expect(metadata.isValid).toBeFalsy();
      });
    });
  });
});
