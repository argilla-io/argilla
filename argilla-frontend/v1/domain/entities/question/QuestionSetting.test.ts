import { QuestionSetting } from "./QuestionSetting";

describe("QuestionSetting", () => {
  describe("suggestionFirst", () => {
    test("return true when options_order is suggestion", () => {
      const setting = new QuestionSetting({ options_order: "suggestion" });
      expect(setting.suggestionFirst).toBeTruthy();
    });
    test("return false when options_order is natural", () => {
      const setting = new QuestionSetting({ options_order: "natural" });
      expect(setting.suggestionFirst).toBeFalsy();
    });
  });

  describe("isEqual", () => {
    test("return false when options_order is different", () => {
      const setting = new QuestionSetting({ options_order: "suggestion" });
      const setting2 = new QuestionSetting({ options_order: "natural" });
      expect(setting.isEqual(setting2)).toBeFalsy();
    });

    test("return false when use_markdown is different", () => {
      const setting = new QuestionSetting({ use_markdown: true });
      const setting2 = new QuestionSetting({ use_markdown: false });
      expect(setting.isEqual(setting2)).toBeFalsy();
    });

    test("return false when visible_options is different", () => {
      const setting = new QuestionSetting({ visible_options: 1 });
      const setting2 = new QuestionSetting({ visible_options: 2 });
      expect(setting.isEqual(setting2)).toBeFalsy();
    });

    test("return false when options are different", () => {
      const setting = new QuestionSetting({ options: ["a"] });
      const setting2 = new QuestionSetting({ options: ["b"] });
      expect(setting.isEqual(setting2)).toBeFalsy();
    });

    test("return false if options are in different positions", () => {
      const setting = new QuestionSetting({ options: ["a", "b"] });
      const setting2 = new QuestionSetting({ options: ["b", "a"] });
      expect(setting.isEqual(setting2)).toBeFalsy();
    });

    test("return true when all properties are the same", () => {
      const setting = new QuestionSetting({
        options_order: "suggestion",
        use_markdown: true,
        visible_options: 1,
        options: ["a"],
      });
      const setting2 = new QuestionSetting({
        options_order: "suggestion",
        use_markdown: true,
        visible_options: 1,
        options: ["a"],
      });
      expect(setting.isEqual(setting2)).toBeTruthy();
    });
  });

  describe("shouldShowVisibleOptions", () => {
    test("return false when options are less than 3", () => {
      const setting = new QuestionSetting({ options: ["a", "b"] });
      expect(setting.shouldShowVisibleOptions).toBeFalsy();
    });

    test("return false when visible_options is not present", () => {
      const setting = new QuestionSetting({ options: ["a", "b", "c"] });
      expect(setting.shouldShowVisibleOptions).toBeFalsy();
    });

    test("return true when options are more than 3 and visible_options is present", () => {
      const setting = new QuestionSetting({
        options: ["a", "b", "c", "d"],
        visible_options: 3,
      });
      expect(setting.shouldShowVisibleOptions).toBeTruthy();
    });
  });
});
