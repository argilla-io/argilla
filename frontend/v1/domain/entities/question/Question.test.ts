import { createTextQuestionMocked } from "../__mocks__/question/mock";

describe("Question", () => {
  describe("restore should", () => {
    test("can restore previous title", () => {
      const question = createTextQuestionMocked();
      const originalTitle = question.title;
      question.title = "NEW TITLE";

      question.restore();

      expect(question.title).toBe(originalTitle);
    });

    test("can restore previous description", () => {
      const question = createTextQuestionMocked();
      const originalDescription = question.description;
      question.description = "NEW DESCRIPTION";

      question.restore();

      expect(question.description).toBe(originalDescription);
    });

    test("can restore previous visible options property", () => {
      const question = createTextQuestionMocked();
      const originalProperty = question.settings.visible_options;
      question.settings.visible_options = 99;

      question.restore();

      expect(question.settings.visible_options).toBe(originalProperty);
    });

    test("can restore previous user markdown property", () => {
      const question = createTextQuestionMocked();
      const originalProperty = question.settings.use_markdown;
      question.settings.use_markdown = false;

      question.restore();

      expect(question.settings.use_markdown).toBe(originalProperty);
    });
  });

  describe("isModified should", () => {
    test("true when title does not match with original", () => {
      const question = createTextQuestionMocked();
      question.title = "NEW TITLE";

      expect(question.isModified).toBeTruthy();
    });

    test("false when title does not match with original", () => {
      const question = createTextQuestionMocked();
      question.title += "       ";

      expect(question.isModified).toBeFalsy();
    });

    test("true when description does not match with original", () => {
      const question = createTextQuestionMocked();
      question.description = "NEW DESCRIPTION";

      expect(question.isModified).toBeTruthy();
    });

    test("false when description does not match with original", () => {
      const question = createTextQuestionMocked();
      question.description += "        ";

      expect(question.isModified).toBeFalsy();
    });

    test("true when use markdown from setting does not match with original", () => {
      const question = createTextQuestionMocked();
      question.settings.use_markdown = false;

      expect(question.isModified).toBeTruthy();
    });

    test("true when visible options from setting does not match with original", () => {
      const question = createTextQuestionMocked();
      question.settings.visible_options = 99;

      expect(question.isModified).toBeTruthy();
    });
  });

  describe("update should", () => {
    test("isModified is false when the question was updated", () => {
      const question = createTextQuestionMocked();
      question.title = "NEW TITLE";

      expect(question.isModified).toBeTruthy();

      question.update();

      expect(question.isModified).toBeFalsy();
    });
  });
});
