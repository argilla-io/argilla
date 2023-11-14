import { createVectorMock } from "../__mocks__/vector/mocks";

describe("Vector", () => {
  describe("restore should", () => {
    test("can restore previous title", () => {
      const vector = createVectorMock("1");
      const originalTitle = vector.title;
      vector.title = "NEW TITLE";

      vector.restore();

      expect(vector.title).toBe(originalTitle);
    });
  });

  describe("isModified should", () => {
    test("true when title does not match with original", () => {
      const vector = createVectorMock("1");
      vector.title = "NEW TITLE";

      expect(vector.isModified).toBeTruthy();
    });

    test("false when title does not match with original", () => {
      const vector = createVectorMock("1");
      vector.title += "       ";

      expect(vector.isModified).toBeFalsy();
    });
  });

  describe("update should", () => {
    test("isModified is false when the vector was updated", () => {
      const FAKE_TITLE_FROM_BACKEND = "TITLE FROM BACKEND";
      const vector = createVectorMock("1");
      vector.title = "NEW TITLE";

      expect(vector.isModified).toBeTruthy();

      vector.update(FAKE_TITLE_FROM_BACKEND);

      expect(vector.isModified).toBeFalsy();
      expect(vector.title).toBe(FAKE_TITLE_FROM_BACKEND);
    });
  });

  describe("vector validation should", () => {
    const invalidLargeTitle =
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum rhoncus mauris sit amet turpis euismod lobortis. Donec sit amet justo non tellus viverra pharetra. Vestibulum vitae aliquet dui. Etiam nec diam cursus, aliquam ligula vitae, volutpat lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Sed et placerat enim. Aenean ut ante dapibus enim tincidunt tempor sed sit amet velit. Quisque vehicula risus quis velit blandit auctor. Maecenas eget accumsan erat.";

    describe("validate should", () => {
      test("return 'This must be less than 500.' error if vector title has more 500 characters", () => {
        const vector = createVectorMock("1");
        vector.title = invalidLargeTitle;
        expect(vector.validate().title).toStrictEqual([
          "This must be less than 500.",
        ]);
      });
      test("don't return error if vector has a valid title", () => {
        const vector = createVectorMock("1");
        vector.title = "TITLE";
        expect(vector.validate().title).toStrictEqual([]);
      });
    });

    describe("is valid", () => {
      test("return true when title is valid", () => {
        const vector = createVectorMock("1");
        vector.title = "TITLE";
        expect(vector.isValid).toBeTruthy();
      });
      test("return false when title is invalid or description is invalid", () => {
        const vector = createVectorMock("1");
        vector.title = invalidLargeTitle;
        expect(vector.isValid).toBeFalsy();
      });
    });
  });
});
