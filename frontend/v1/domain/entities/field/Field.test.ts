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
      const field = createTextFieldMock("1");
      field.title = "NEW TITLE";

      expect(field.isModified).toBeTruthy();

      field.update();

      expect(field.isModified).toBeFalsy();
    });
  });
});
