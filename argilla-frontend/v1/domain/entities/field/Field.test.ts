import { createTextFieldMock } from "../__mocks__/field/mocks";

describe("Field", () => {
  describe("restore should", () => {
    test("can restore previous title", () => {
      const field = createTextFieldMock("1");
      const originalTitle = field.title;
      field.title = "NEW TITLE";

      field.restore();

      expect(field.title).toBe(originalTitle);
    });

    test("can restore previous user markdown property", () => {
      const field = createTextFieldMock("1");
      const originalProperty = field.settings.use_markdown;
      field.settings.use_markdown = false;

      field.restore();

      expect(field.settings.use_markdown).toBe(originalProperty);
    });
  });

  describe("isModified should", () => {
    test("true when title does not match with original", () => {
      const field = createTextFieldMock("1");
      field.title = "NEW TITLE";

      expect(field.isModified).toBeTruthy();
    });

    test("false when title does not match with original", () => {
      const field = createTextFieldMock("1");
      field.title += "       ";

      expect(field.isModified).toBeFalsy();
    });

    test("true when use markdown from setting does not match with original", () => {
      const field = createTextFieldMock("1");
      field.settings.use_markdown = false;

      expect(field.isModified).toBeTruthy();
    });
  });

  describe("update should", () => {
    test("isModified is false when the field was updated", () => {
      const FAKE_TITLE_FROM_BACKEND = "TITLE FROM BACKEND";
      const field = createTextFieldMock("1");
      field.title = "NEW TITLE";

      expect(field.isModified).toBeTruthy();

      field.update(FAKE_TITLE_FROM_BACKEND, {});

      expect(field.isModified).toBeFalsy();
      expect(field.title).toBe(FAKE_TITLE_FROM_BACKEND);
    });
  });

  describe("field validation should", () => {
    const invalidLargeTitle =
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum rhoncus mauris sit amet turpis euismod lobortis. Donec sit amet justo non tellus viverra pharetra. Vestibulum vitae aliquet dui. Etiam nec diam cursus, aliquam ligula vitae, volutpat lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Sed et placerat enim. Aenean ut ante dapibus enim tincidunt tempor sed sit amet velit. Quisque vehicula risus quis velit blandit auctor. Maecenas eget accumsan erat.";

    describe("validate should", () => {
      test("return 'This must be less than 500.' error if field title has more 500 characters", () => {
        const field = createTextFieldMock("1");
        field.title = invalidLargeTitle;
        expect(field.validate().title).toStrictEqual([
          "This must be less than 500.",
        ]);
      });
      test("don't return error if field has a valid title", () => {
        const field = createTextFieldMock("1");
        field.title = "TITLE";
        expect(field.validate().title).toStrictEqual([]);
      });
    });

    describe("is field valid", () => {
      test("return true when title is valid", () => {
        const field = createTextFieldMock("1");
        field.title = "TITLE";
        expect(field.isFieldValid).toBeTruthy();
      });
      test("return false when title is invalid or description is invalid", () => {
        const field = createTextFieldMock("1");
        field.title = invalidLargeTitle;
        expect(field.isFieldValid).toBeFalsy();
      });
    });
  });
});
