import {
  createLabelQuestionMocked,
  createTextQuestionMocked,
} from "../__mocks__/question/mock";

describe("Question", () => {
  describe("initialize should", () => {
    test("initialize visible options with same options length in case that visible options comes as null", () => {
      const question = createLabelQuestionMocked({
        visible_options: null,
      });

      expect(question.settings.visible_options).toBe(
        question.settings.options.length
      );
    });

    test("no modify visible options prop if is already defined", () => {
      const question = createLabelQuestionMocked({
        visible_options: 99,
      });

      expect(question.settings.visible_options).toBe(99);
    });
  });

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

    test("isModified is false when the question was loaded with response", () => {
      const question = createTextQuestionMocked();

      question.response({ value: "positive" });

      expect(question.isModified).toBeFalsy();
    });

    test("isModified is true when the question was loaded with response  and modified after initialization", () => {
      const question = createTextQuestionMocked();
      question.response({ value: "positive" });

      question.title = "NEW TITLE";

      expect(question.isModified).toBeTruthy();
    });
  });

  describe("question validation should", () => {
    const invalidLargeDescription =
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum rhoncus mauris sit amet turpis euismod lobortis. Donec sit amet justo non tellus viverra pharetra. Vestibulum vitae aliquet dui. Etiam nec diam cursus, aliquam ligula vitae, volutpat lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Sed et placerat enim. Aenean ut ante dapibus enim tincidunt tempor sed sit amet velit. Quisque vehicula risus quis velit blandit auctor. Maecenas eget accumsan erat.";
    const invalidLargeTitle =
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum rhoncus mauris sit amet turpis euismod lobortis. Donec sit amet justo non tellus viverra pharetra. Vestibulum vitae aliquet dui. Etia.";

    describe("validate should", () => {
      test("return 'This field is required.' error if question title is empty", () => {
        const question = createTextQuestionMocked();
        question.title = "";
        expect(question.validate().title).toStrictEqual([
          "This field is required.",
        ]);
      });
      test("return 'This must be less than 200.' error if question title has more 200 characters", () => {
        const question = createTextQuestionMocked();
        question.title = invalidLargeTitle;
        expect(question.validate().title).toStrictEqual([
          "This must be less than 200.",
        ]);
      });
      test("return 'This must be less than 500.' error if question description has more 200 characters", () => {
        const question = createTextQuestionMocked();
        question.description = invalidLargeDescription;
        expect(question.validate().description).toStrictEqual([
          "This must be less than 500.",
        ]);
      });
      test("don't return error if question has title", () => {
        const question = createTextQuestionMocked();
        question.title = "TITLE";
        expect(question.validate().title).toStrictEqual([]);
      });
      test("don't return error if question has description", () => {
        const question = createTextQuestionMocked();
        question.description = "DESCRIPTION";
        expect(question.validate().description).toStrictEqual([]);
      });
    });

    describe("is question valid", () => {
      test("return true when title and description are valid", () => {
        const question = createTextQuestionMocked();
        question.title = "DESCRIPTION";
        question.description = "DESCRIPTION";
        expect(question.isQuestionValid).toBeTruthy();
      });
      test("return false when title is invalid or description is invalid", () => {
        const question = createTextQuestionMocked();
        question.title = "";
        question.description = invalidLargeDescription;
        expect(question.isQuestionValid).toBeFalsy();
      });
      test("is true when the user set description as a null", () => {
        const question = createTextQuestionMocked();
        question.description = null;
        expect(question.isQuestionValid).toBeTruthy();
      });
    });
  });
});
