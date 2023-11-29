import { SuggestionCriteria } from "./SuggestionCriteria";

describe("SuggestionCriteria", () => {
  test("should be able to parse url params with two suggestions, both with score and values", () => {
    const criteria = new SuggestionCriteria();
    criteria.complete(
      "content_class.score.ge0.le0.24~content_class.value.operator.and.values.hate.pii~relevant.score.ge0.le0.18~relevant.value.values.Yes.No"
    );

    expect(criteria.value).toEqual([
      {
        name: "content_class",
        value: [
          {
            name: "score",
            value: {
              ge: 0,
              le: 0.24,
            },
          },
          {
            name: "value",
            value: {
              operator: "and",
              values: ["hate", "pii"],
            },
          },
        ],
      },
      {
        name: "relevant",
        value: [
          {
            name: "score",
            value: {
              ge: 0,
              le: 0.18,
            },
          },
          {
            name: "value",
            value: {
              values: ["Yes", "No"],
            },
          },
        ],
      },
    ]);
  });

  test("should be able to parse url params with two suggestions, both with score and values and agent", () => {
    const criteria = new SuggestionCriteria();
    criteria.complete(
      "content_class.score.ge0.le0.24~content_class.value.operator.and.values.hate.pii~content_class.agent.chat-gtp~relevant.score.ge0.le0.18~relevant.value.values.Yes.No~relevant.agent.1.2.3"
    );

    expect(criteria.value).toEqual([
      {
        name: "content_class",
        value: [
          {
            name: "score",
            value: {
              ge: 0,
              le: 0.24,
            },
          },
          {
            name: "value",
            value: {
              operator: "and",
              values: ["hate", "pii"],
            },
          },
          {
            name: "agent",
            value: ["chat-gtp"],
          },
        ],
      },
      {
        name: "relevant",
        value: [
          {
            name: "score",
            value: {
              ge: 0,
              le: 0.18,
            },
          },
          {
            name: "value",
            value: {
              values: ["Yes", "No"],
            },
          },
          {
            name: "agent",
            value: ["1", "2", "3"],
          },
        ],
      },
    ]);
  });

  test("should be able to parse url params with values with operator", () => {
    const criteria = new SuggestionCriteria();
    criteria.complete("content_class.value.operator.and.values.hate.pii");

    expect(criteria.value).toEqual([
      {
        name: "content_class",
        value: [
          {
            name: "value",
            value: {
              operator: "and",
              values: ["hate", "pii"],
            },
          },
        ],
      },
    ]);
  });

  test("should be able to parse url params with values without operator", () => {
    const criteria = new SuggestionCriteria();
    criteria.complete("content_class.value.values.hate.pii");

    expect(criteria.value).toEqual([
      {
        name: "content_class",
        value: [
          {
            name: "value",
            value: {
              values: ["hate", "pii"],
            },
          },
        ],
      },
    ]);
    expect("operator" in criteria.value[0].value[0].value).toBeFalsy();
  });

  test("should be able to parse url params with value as range for rating questions", () => {
    const criteria = new SuggestionCriteria();
    criteria.complete("rating.value.ge1.le3");
    expect(criteria.value).toEqual([
      {
        name: "rating",
        value: [
          {
            name: "value",
            value: {
              ge: 1,
              le: 3,
            },
          },
        ],
      },
    ]);
  });
});
