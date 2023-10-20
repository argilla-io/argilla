import { RecordCriteria } from "./RecordCriteria";

describe("RecordCriteria", () => {
  describe("isFilteringByText", () => {
    test("should return true if searchText is not empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "searchText",
        [],
        []
      );

      expect(criteria.isFilteringByText).toBe(true);
    });

    test("should return false if searchText is empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "",
        [],
        []
      );

      expect(criteria.isFilteringByText).toBe(false);
    });

    test("should return false if searchText is undefined", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        undefined,
        [],
        []
      );

      expect(criteria.isFilteringByText).toBe(false);
    });
  });

  describe("isFilteringByMetadata should", () => {
    test("return true if metadata is not empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "",
        ["metadata"],
        []
      );

      expect(criteria.isFilteringByMetadata).toBe(true);
    });

    test("return false if metadata is empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "",
        [],
        []
      );

      expect(criteria.isFilteringByMetadata).toBe(false);
    });

    test("return false if metadata is undefined", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "",
        undefined,
        []
      );

      expect(criteria.isFilteringByMetadata).toBe(false);
    });
  });

  describe("hasChanges should", () => {
    test("return true if page is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "",
        [],
        []
      );

      criteria.page = 2;

      expect(criteria.hasChanges).toBe(true);
    });

    test("return true if status is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "",
        [],
        []
      );

      criteria.status = "submitted";

      expect(criteria.hasChanges).toBe(true);
    });

    test("return true if searchText is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "Can AI help us?",
        [],
        []
      );

      criteria.searchText = "Can ML help to improve your business processes?";

      expect(criteria.hasChanges).toBe(true);
    });

    test("return true if metadata is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "",
        ["metadata"],
        []
      );

      criteria.metadata = ["metadata1", "metadata2"];

      expect(criteria.hasChanges).toBe(true);
    });

    test("return true if sortBy is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "",
        [],
        ["sortBy"]
      );

      criteria.sortBy = ["sortBy1", "sortBy2"];

      expect(criteria.hasChanges).toBe(true);
    });

    test("return false if page, status, searchText, metadata or sortBy  are same after commit", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "",
        [],
        []
      );

      criteria.page = 2;
      criteria.status = "submitted";
      criteria.searchText = "Love ML";
      criteria.metadata = ["metadata1", "metadata2"];
      criteria.sortBy = ["sortBy1", "sortBy2"];
      criteria.commit();

      expect(criteria.hasChanges).toBe(false);
    });
  });

  describe("Reset should", () => {
    test("restore committed changes", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        1,
        "pending",
        "Do you love ML?",
        ["metadata.your_feel"],
        ["inserted_at:asc"]
      );

      criteria.page = 1;
      criteria.status = "discarded";
      criteria.searchText = "Do you love AI?";
      criteria.metadata = ["metadata.my_feel"];
      criteria.sortBy = ["inserted_at:desc"];

      criteria.reset();

      expect(criteria.page).toEqual(criteria.committed.page);
      expect(criteria.status).toEqual(criteria.committed.status);
      expect(criteria.searchText).toEqual(criteria.committed.searchText);
      expect(criteria.metadata).toEqual(criteria.committed.metadata);
      expect(criteria.sortBy).toEqual(criteria.committed.sortBy);
    });
  });
});
