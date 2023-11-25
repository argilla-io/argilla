import { SortCriteria } from "./SortCriteria";

describe("SortCriteria", () => {
  test("should be able to parse url params with two sorts without property", () => {
    const criteria = new SortCriteria();
    criteria.complete("record.inserted_at.asc~record.updated_at.desc");
    expect(criteria.value).toEqual([
      {
        entity: "record",
        name: "inserted_at",
        order: "asc",
      },
      {
        entity: "record",
        name: "updated_at",
        order: "desc",
      },
    ]);
  });

  test("should be able to parse url params with two sorts with property", () => {
    const criteria = new SortCriteria();
    criteria.complete("suggestion.relevant.score.asc~record.updated_at.desc");
    expect(criteria.value).toEqual([
      {
        entity: "suggestion",
        name: "relevant",
        property: "score",
        order: "asc",
      },
      {
        entity: "record",
        name: "updated_at",
        order: "desc",
      },
    ]);
  });
});
