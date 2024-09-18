import { QuestionType } from "./QuestionType";

describe("QuestionType should", () => {
  describe("from should", () => {
    test("create a new instance of QuestionType", () => {
      const type = QuestionType.from("ranking");
      expect(type).toBeInstanceOf(QuestionType);
    });
  });
  describe("isRankingType should", () => {
    test("return true when type is ranking", () => {
      const type = QuestionType.from("ranking");
      expect(type.isRankingType).toBeTruthy();
    });
    test("return false when type is not ranking", () => {
      const type = QuestionType.from("multi_label_selection");
      expect(type.isRankingType).toBeFalsy();
    });
  });
  describe("isMultiLabelType should", () => {
    test("return true when type is multi_label_selection", () => {
      const type = QuestionType.from("multi_label_selection");
      expect(type.isMultiLabelType).toBeTruthy();
    });
    test("return false when type is not multi_label_selection", () => {
      const type = QuestionType.from("ranking");
      expect(type.isMultiLabelType).toBeFalsy();
    });
  });
  describe("isSingleLabelType should", () => {
    test("return true when type is label_selection", () => {
      const type = QuestionType.from("label_selection");
      expect(type.isSingleLabelType).toBeTruthy();
    });
    test("return false when type is not label_selection", () => {
      const type = QuestionType.from("ranking");
      expect(type.isSingleLabelType).toBeFalsy();
    });
  });
  describe("isTextType should", () => {
    test("return true when type is text", () => {
      const type = QuestionType.from("text");
      expect(type.isTextType).toBeTruthy();
    });
    test("return false when type is not text", () => {
      const type = QuestionType.from("ranking");
      expect(type.isTextType).toBeFalsy();
    });
  });
  describe("isSpanType should", () => {
    test("return true when type is span", () => {
      const type = QuestionType.from("span");
      expect(type.isSpanType).toBeTruthy();
    });
    test("return false when type is not span", () => {
      const type = QuestionType.from("ranking");
      expect(type.isSpanType).toBeFalsy();
    });
  });
});
