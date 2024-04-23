import { QuestionType } from "./QuestionType";
import { Suggestion } from "./Suggestion";

describe("Suggestion", () => {
  describe("single label type", () => {
    test("return true if the answer is suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("label_selection"),
        "suggestedAnswer",
        1,
        "agent"
      );
      const isSuggested = suggestion.isSuggested("suggestedAnswer");
      expect(isSuggested).toBe(true);

      const suggested = suggestion.getSuggestion("suggestedAnswer");
      expect(suggested).toEqual({
        value: "suggestedAnswer",
        score: 1,
        agent: "agent",
      });
    });

    test("return false if the answer is not suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("label_selection"),
        "suggestedAnswer",
        1,
        "agent"
      );

      const isSuggested = suggestion.isSuggested("notSuggestedAnswer");
      expect(isSuggested).toBe(false);
    });
  });

  describe("text type", () => {
    test("return true if the answer is suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("text"),
        "Suggested text",
        1,
        "agent"
      );
      const isSuggested = suggestion.isSuggested("Suggested text");
      expect(isSuggested).toBe(true);

      const suggested = suggestion.getSuggestion("Suggested text");
      expect(suggested).toEqual({
        value: "Suggested text",
        score: 1,
        agent: "agent",
      });
    });

    test("return false if the answer is not suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("text"),
        "suggestedAnswer",
        1,
        "agent"
      );

      const isSuggested = suggestion.isSuggested("notSuggestedAnswer");
      expect(isSuggested).toBe(false);
    });
  });

  describe("multi label type", () => {
    test("return true if the answer is suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("multi_label_selection"),
        ["One", "Two"],
        [0.2, 0.3],
        "agent"
      );

      const isSuggested = suggestion.isSuggested("One");
      expect(isSuggested).toBe(true);

      const suggested = suggestion.getSuggestion("One");
      expect(suggested).toEqual({
        value: "One",
        score: 0.2,
        agent: "agent",
      });

      const isSuggestedTwo = suggestion.isSuggested("Two");
      expect(isSuggestedTwo).toBe(true);

      const suggestedTwo = suggestion.getSuggestion("Two");
      expect(suggestedTwo).toEqual({
        value: "Two",
        score: 0.3,
        agent: "agent",
      });
    });

    test("return false if the answer is not suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("multi_label_selection"),
        ["One", "Two"],
        [1],
        "agent"
      );

      const isSuggested = suggestion.isSuggested("Three");
      expect(isSuggested).toBe(false);
    });

    test("score should be undefined if not provided", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("multi_label_selection"),
        ["One", "Two"],
        undefined,
        "agent"
      );

      const isSuggested = suggestion.isSuggested("One");
      expect(isSuggested).toBe(true);

      const suggested = suggestion.getSuggestion("One");
      expect(suggested).toEqual({
        value: "One",
        score: undefined,
        agent: "agent",
      });
    });
  });

  describe("rating type", () => {
    test("return true if the answer is suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("rating"),
        5,
        1,
        "agent"
      );

      const isSuggested = suggestion.isSuggested(5);
      expect(isSuggested).toBe(true);

      const suggested = suggestion.getSuggestion(5);
      expect(suggested).toEqual({
        value: 5,
        score: 1,
        agent: "agent",
      });
    });

    test("return false if the answer is not suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("rating"),
        5,
        1,
        "agent"
      );

      const isSuggested = suggestion.isSuggested(3);
      expect(isSuggested).toBe(false);
    });
  });

  describe("ranking type", () => {
    test("return true if the answer is suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("ranking"),
        [
          { value: "One", rank: 1 },
          { value: "Two", rank: 2 },
        ],
        [0.2, 0.3],
        "agent"
      );

      const isSuggested = suggestion.isSuggested({
        value: "One",
        rank: 1,
      });
      expect(isSuggested).toBe(true);

      const suggested = suggestion.getSuggestion({
        value: "One",
        rank: 1,
      });
      expect(suggested).toEqual({
        value: {
          value: "One",
          rank: 1,
        },
        score: 0.2,
        agent: "agent",
      });

      const isSuggestedTwo = suggestion.isSuggested({
        value: "Two",
        rank: 2,
      });
      expect(isSuggestedTwo).toBe(true);

      const suggestedTwo = suggestion.getSuggestion({
        value: "Two",
        rank: 2,
      });
      expect(suggestedTwo).toEqual({
        value: {
          value: "Two",
          rank: 2,
        },
        score: 0.3,
        agent: "agent",
      });
    });

    test("return false if the answer is not suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("ranking"),
        [
          { value: "One", rank: 1 },
          { value: "Two", rank: 2 },
        ],
        [0.2, 0.3],
        "agent"
      );

      const isSuggested = suggestion.isSuggested({
        value: "Three",
        rank: 3,
      });
      expect(isSuggested).toBe(false);
    });

    test("score should be undefined if not provided", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("ranking"),
        [
          { value: "One", rank: 1 },
          { value: "Two", rank: 2 },
        ],
        undefined,
        "agent"
      );

      const isSuggested = suggestion.isSuggested({
        value: "One",
        rank: 1,
      });
      expect(isSuggested).toBe(true);

      const suggested = suggestion.getSuggestion({
        value: "One",
        rank: 1,
      });
      expect(suggested).toEqual({
        value: {
          value: "One",
          rank: 1,
        },
        score: undefined,
        agent: "agent",
      });
    });
  });

  describe("Span type", () => {
    test("return true if the answer is suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("span"),
        [
          {
            start: 0,
            end: 5,
            label: "One",
          },
          {
            start: 0,
            end: 5,
            label: "Two",
          },
        ],
        [0.2, 0.3],
        "agent"
      );
      const isSuggested = suggestion.isSuggested({
        start: 0,
        end: 5,
        label: "Two",
      });
      expect(isSuggested).toBe(true);

      const suggested = suggestion.getSuggestion({
        start: 0,
        end: 5,
        label: "Two",
      });
      expect(suggested).toEqual({
        value: {
          start: 0,
          end: 5,
          label: "Two",
        },
        score: 0.3,
        agent: "agent",
      });
    });

    test("return false if the answer is not suggested", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("span"),
        [
          {
            start: 0,
            end: 5,
            label: "One",
          },
          {
            start: 0,
            end: 5,
            label: "Two",
          },
        ],
        [0.2, 0.3],
        "agent"
      );

      const isSuggested = suggestion.isSuggested({
        start: 0,
        end: 5,
        label: "Three",
      });
      expect(isSuggested).toBe(false);
    });

    test("score should be undefined if not provided", () => {
      const suggestion = new Suggestion(
        "id",
        "questionId",
        QuestionType.from("span"),
        [
          {
            start: 0,
            end: 5,
            label: "One",
          },
          {
            start: 0,
            end: 5,
            label: "Two",
          },
        ],
        undefined,
        "agent"
      );

      const isSuggested = suggestion.isSuggested({
        start: 0,
        end: 5,
        label: "One",
      });
      expect(isSuggested).toBe(true);

      const suggested = suggestion.getSuggestion({
        start: 0,
        end: 5,
        label: "One",
      });
      expect(suggested).toEqual({
        value: {
          start: 0,
          end: 5,
          label: "One",
        },
        score: undefined,
        agent: "agent",
      });
    });
  });
});
