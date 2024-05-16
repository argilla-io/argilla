import { SpanAnswer } from "../../IAnswer";
import { SpanQuestionAnswer } from "../QuestionAnswer";
import { QuestionType } from "../QuestionType";

describe("Span answer", () => {
  describe("response", () => {
    test("should set the answer", () => {
      const spanAnswer = new SpanQuestionAnswer(
        QuestionType.from("span"),
        "QUESTION_NAME",
        [
          {
            value: "value",
            color: "color",
            text: "text",
          },
        ]
      );

      const answer: SpanAnswer[] = [
        {
          end: 1,
          start: 0,
          label: "label",
        },
      ];

      spanAnswer.response({
        value: answer,
      });

      expect(spanAnswer.valuesAnswered).toEqual(answer);
    });
  });

  describe("clear", () => {
    test("should clear the value", () => {
      const spanAnswer = new SpanQuestionAnswer(
        QuestionType.from("span"),
        "QUESTION_NAME",
        [
          {
            value: "value",
            color: "color",
            text: "text",
          },
        ]
      );
      const answer: SpanAnswer[] = [
        {
          end: 1,
          start: 0,
          label: "label",
        },
      ];

      spanAnswer.response({
        value: answer,
      });

      spanAnswer.clear();

      expect(spanAnswer.valuesAnswered).toEqual([]);
    });
  });

  describe("isValid", () => {
    test("should return true if value is not empty", () => {
      const spanAnswer = new SpanQuestionAnswer(
        QuestionType.from("span"),
        "QUESTION_NAME",
        [
          {
            value: "value",
            color: "color",
            text: "text",
          },
        ]
      );

      expect(spanAnswer.isValid).toBe(true);
    });
  });
});
