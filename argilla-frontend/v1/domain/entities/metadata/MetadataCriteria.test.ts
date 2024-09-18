import { MetadataCriteria } from "./MetadataCriteria";

describe("MetadataCriteria", () => {
  test("should be able to parse url params for float score metadata", () => {
    const criteria = new MetadataCriteria();
    criteria.complete("metadata.ge0.le0.24");

    expect(criteria.value).toEqual([
      {
        name: "metadata",
        value: {
          ge: 0,
          le: 0.24,
        },
      },
    ]);
  });

  test("should be able to parse url params for negative float score metadata", () => {
    const criteria = new MetadataCriteria();
    criteria.complete("metadata.ge-3.le-0.24");

    expect(criteria.value).toEqual([
      {
        name: "metadata",
        value: {
          ge: -3,
          le: -0.24,
        },
      },
    ]);
  });

  test("should be able to parse url params for integer score metadata", () => {
    const criteria = new MetadataCriteria();
    criteria.complete("metadata.ge2.le24");

    expect(criteria.value).toEqual([
      {
        name: "metadata",
        value: {
          ge: 2,
          le: 24,
        },
      },
    ]);
  });

  test("should be able to parse url params for options metadata", () => {
    const criteria = new MetadataCriteria();
    criteria.complete("metadata.Yes.No");

    expect(criteria.value).toEqual([
      {
        name: "metadata",
        value: ["Yes", "No"],
      },
    ]);
  });

  test("should be able to parse url params for options numbers metadata", () => {
    const criteria = new MetadataCriteria();
    criteria.complete("metadata.1.2.3");

    expect(criteria.value).toEqual([
      {
        name: "metadata",
        value: ["1", "2", "3"],
      },
    ]);
  });

  test("should be able to parse url params for options and score metadata", () => {
    const criteria = new MetadataCriteria();
    criteria.complete("metadata1.ge0.le0.24~metadata2.Yes.No");

    expect(criteria.value).toEqual([
      {
        name: "metadata1",
        value: {
          ge: 0,
          le: 0.24,
        },
      },
      {
        name: "metadata2",
        value: ["Yes", "No"],
      },
    ]);
  });
});
