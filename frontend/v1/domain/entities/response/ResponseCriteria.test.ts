import { ResponseCriteria } from "./ResponseCriteria";

describe("ResponseCriteria", () => {
  test("should be able to parse url params for float score response", () => {
    const criteria = new ResponseCriteria();
    criteria.complete("response.ge0.le0.24");

    expect(criteria.value).toEqual([
      {
        name: "response",
        value: {
          ge: 0,
          le: 0.24,
        },
      },
    ]);
  });

  test("should be able to parse url params for negative float score response", () => {
    const criteria = new ResponseCriteria();
    criteria.complete("response.ge-3.le-0.24");

    expect(criteria.value).toEqual([
      {
        name: "response",
        value: {
          ge: -3,
          le: -0.24,
        },
      },
    ]);
  });

  test("should be able to parse url params for integer score response", () => {
    const criteria = new ResponseCriteria();
    criteria.complete("response.ge2.le24");

    expect(criteria.value).toEqual([
      {
        name: "response",
        value: {
          ge: 2,
          le: 24,
        },
      },
    ]);
  });

  test("should be able to parse url params for options response", () => {
    const criteria = new ResponseCriteria();
    criteria.complete("response.Yes.No");

    expect(criteria.value).toEqual([
      {
        name: "response",
        value: ["Yes", "No"],
      },
    ]);
  });

  test("should be able to parse url params for options numbers response", () => {
    const criteria = new ResponseCriteria();
    criteria.complete("response.1.2.3");

    expect(criteria.value).toEqual([
      {
        name: "response",
        value: ["1", "2", "3"],
      },
    ]);
  });

  test("should be able to parse url params for options and score response", () => {
    const criteria = new ResponseCriteria();
    criteria.complete("response1.ge0.le0.24~response2.Yes.No");

    expect(criteria.value).toEqual([
      {
        name: "response1",
        value: {
          ge: 0,
          le: 0.24,
        },
      },
      {
        name: "response2",
        value: ["Yes", "No"],
      },
    ]);
  });

  test("should be able to parse url params for options with operator", () => {
    const criteria = new ResponseCriteria();
    criteria.complete("multi-label.operator.or.values.label2.label3.label4");

    expect(criteria.value).toEqual([
      {
        name: "multi-label",
        value: {
          operator: "or",
          values: ["label2", "label3", "label4"],
        },
      },
    ]);
  });

  test("should be able to parse url params for options with operator", () => {
    const criteria = new ResponseCriteria();
    criteria.complete("multi-label.operator.and.values.label2.label3.label4");

    expect(criteria.value).toEqual([
      {
        name: "multi-label",
        value: {
          operator: "and",
          values: ["label2", "label3", "label4"],
        },
      },
    ]);
  });
});
