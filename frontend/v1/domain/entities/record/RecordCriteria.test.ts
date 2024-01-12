import { RecordCriteria } from "./RecordCriteria";

describe("RecordCriteria", () => {
  describe("isFilteringByText", () => {
    test("should return true if searchText is not empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "searchText",
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteringByText).toBe(true);
    });

    test("should return false if searchText is empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteringByText).toBe(false);
    });

    test("should return false if searchText is undefined", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        undefined,
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteringByText).toBe(false);
    });
  });

  describe("isFilteringBySimilarity", () => {
    test("should return true if similaritySearch is not empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        "record.1.vector.2.limit.50.order.most"
      );

      expect(criteria.isFilteringBySimilarity).toBe(true);
    });

    test("should return false if similaritySearch is empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteringBySimilarity).toBe(false);
    });
  });

  describe("isFilteringByResponse", () => {
    test("should return true if response is range", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "response.ge.1le.5",
        "",
        null
      );

      expect(criteria.isFilteringByResponse).toBe(true);
    });

    test("should return true if response is terms", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "response.option1~option2",
        "",
        null
      );

      expect(criteria.isFilteringByResponse).toBe(true);
    });

    test("should return false if response is empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteringByResponse).toBe(false);
    });
  });

  describe("isFilteringBySuggestion", () => {
    test("should return true if suggestion is not empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "content_class.value.operator.and.values.hate.pii",
        null
      );

      expect(criteria.isFilteringBySuggestion).toBe(true);
    });

    test("should return false if suggestion is empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteringBySuggestion).toBe(false);
    });
  });

  describe("isSortingBy", () => {
    test("should return true if sortBy is not empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "suggestion.relevant.score.asc",
        "",
        "",
        null
      );

      expect(criteria.isSortingBy).toBe(true);
    });

    test("should return false if sortBy is empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isSortingBy).toBe(false);
    });
  });

  describe("isFilteredByText", () => {
    test("should return true if searchText is not empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "searchText",
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteredByText).toBe(true);
    });

    test("should return false if searchText is empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteredByText).toBe(false);
    });

    test("should return false if searchText is undefined", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        undefined,
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteredByText).toBe(false);
    });
  });

  describe("isFilteredByMetadata should", () => {
    test("return true if metadata is range", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "metadata.ge.1le.5",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteredByMetadata).toBe(true);
    });

    test("return true if metadata is terms", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "metadata.option1~option2",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteredByMetadata).toBe(true);
    });

    test("return false if metadata is empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteredByMetadata).toBe(false);
    });

    test("return false if metadata is undefined", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        undefined,
        "",
        "",
        "",
        null
      );

      expect(criteria.isFilteredByMetadata).toBe(false);
    });
  });

  describe("isFilteredByResponse", () => {
    test("should return true if response is range", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "response.ge.1le.5",
        "",
        null
      );

      expect(criteria.isFilteredByResponse).toBe(true);
    });

    test("should return true if response is terms", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "response.option1~option2",
        "",
        null
      );

      expect(criteria.isFilteredByResponse).toBe(true);
    });
  });

  describe("isFilteredBySuggestion", () => {
    test("should return true if suggestion is not empty", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "content_class.score.ge0.le0.24",
        null
      );

      expect(criteria.isFilteredBySuggestion).toBe(true);
    });
  });

  describe("hasChanges should", () => {
    test("return true if page is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      criteria.page.goTo(2);

      expect(criteria.hasChanges).toBe(true);
    });

    test("return true if status is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      criteria.status = "submitted";

      expect(criteria.hasChanges).toBe(true);
    });

    test("return true if searchText is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "Can AI help us?",
        "",
        "",
        "",
        "",
        null
      );

      criteria.searchText = "Can ML help to improve your business processes?";

      expect(criteria.hasChanges).toBe(true);
    });

    test("return true if metadata is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      criteria.metadata.complete("your_feel.happy~sad");

      expect(criteria.hasChanges).toBe(true);
    });

    test("return true if sortBy is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      criteria.sortBy.complete(
        JSON.stringify([
          {
            entity: "record",
            name: "inserted_at",
            order: "asc",
          },
        ])
      );

      expect(criteria.hasChanges).toBe(true);
    });

    test("return true if similaritySearch is different", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        "record.1.vector.2.limit.50.order.most"
      );

      criteria.similaritySearch.order = "least";

      expect(criteria.hasChanges).toBe(true);
    });

    test("return false if page, status, searchText, metadata, sortBy or similaritySearch are same after commit", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );

      criteria.page.goTo(2);
      criteria.status = "submitted";
      criteria.searchText = "Love ML";
      criteria.metadata.value = [
        { name: "metadata1", value: ["value1"] },
        { name: "metadata2", value: ["value2"] },
      ];
      criteria.sortBy.value = [
        { entity: "record", name: "inserted_at", order: "asc" },
      ];

      criteria.similaritySearch.order = "least";
      criteria.similaritySearch.recordId = "1";
      criteria.similaritySearch.vectorName = "2";
      criteria.similaritySearch.limit = 50;

      criteria.commit();

      expect(criteria.hasChanges).toBe(false);
    });
  });

  describe("rollback should", () => {
    test("restore committed changes", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "Do you love ML?",
        "your_feel.happy~sad",
        "inserted_at:desc",
        "",
        "",
        "record:1,vector:2,limit:50,order:most"
      );

      criteria.page.goTo(1);
      criteria.status = "discarded";
      criteria.searchText = "Do you love AI?";
      criteria.metadata.complete("your_feel.sad");
      criteria.sortBy.complete("record.inserted_at.asc");
      criteria.similaritySearch.order = "least";

      criteria.rollback();

      expect(criteria.page).toEqual(criteria.committed.page);
      expect(criteria.status).toEqual(criteria.committed.status);
      expect(criteria.searchText).toEqual(criteria.committed.searchText);
      expect(criteria.metadata).toEqual(criteria.committed.metadata);
      expect(criteria.sortBy).toEqual(criteria.committed.sortBy);
      expect(criteria.similaritySearch).toEqual(
        criteria.committed.similaritySearch
      );
    });
  });

  describe("nextPage", () => {
    test("should increment page focus mode", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "Do you love ML?",
        "your_feel.happy~sad",
        "inserted_at:desc",
        "",
        "",
        "record:1,vector:2,limit:50,order:most"
      );

      criteria.nextPage();

      expect(criteria.page.client.page).toEqual(2);
    });

    test("should increment page bulk mode", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1",
        "pending",
        "Do you love ML?",
        "your_feel.happy~sad",
        "inserted_at:desc",
        "",
        "",
        "record:1,vector:2,limit:50,order:most"
      );

      criteria.page.mode = "bulk";
      criteria.page.client.many = 10;
      criteria.commit();

      criteria.nextPage();

      expect(criteria.page.client.page).toEqual(11);
    });
  });

  describe("previousPage", () => {
    test("should decrement page", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "3",
        "pending",
        "Do you love ML?",
        "your_feel.happy~sad",
        "inserted_at:desc",
        "",
        "",
        "record:1,vector:2,limit:50,order:most"
      );

      criteria.previousPage();

      expect(criteria.page.client.page).toEqual(2);
    });

    test("should decrement page bulk mode", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "11",
        "pending",
        "Do you love ML?",
        "your_feel.happy~sad",
        "inserted_at:desc",
        "",
        "",
        "record:1,vector:2,limit:50,order:most"
      );

      criteria.page.mode = "bulk";
      criteria.page.client.many = 10;
      criteria.commit();

      criteria.previousPage();

      expect(criteria.page.client.page).toEqual(1);
    });
  });

  describe("isComingToBulkMode", () => {
    test("should return true when previous mode has focus and now is bulk", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "3",
        "pending",
        "",
        "",
        "",
        "",
        "",
        ""
      );

      criteria.page.bulkMode();

      criteria.commit();

      expect(criteria.isComingToBulkMode).toBeTruthy();
    });

    test("should return true when the criteria does not have any change", () => {
      const criteria = new RecordCriteria(
        "datasetId",
        "1~10",
        "pending",
        "",
        "",
        "",
        "",
        "",
        ""
      );

      criteria.commit();

      expect(criteria.isComingToBulkMode).toBeTruthy();
    });
  });
});
