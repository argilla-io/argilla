import { SimilarityCriteria } from "./SimilarityCriteria";

describe("SimilarityCriteria ", () => {
  describe("reset should", () => {
    test("set default criteria values", () => {
      const criteria = new SimilarityCriteria();
      criteria.recordId = "recordId";
      criteria.vectorName = "vectorName";
      criteria.limit = 50;
      criteria.order = "least";

      criteria.reset();

      expect(criteria.recordId).toBeUndefined();
      expect(criteria.vectorName).toBeUndefined();
      expect(criteria.limit).toBe(50);
      expect(criteria.order).toBe("most");
    });
  });

  describe("isCompleted should", () => {
    test("return true when all criteria are defined", () => {
      const criteria = new SimilarityCriteria();
      criteria.recordId = "recordId";
      criteria.vectorName = "vectorName";
      criteria.limit = 50;
      criteria.order = "least";

      expect(criteria.isCompleted).toBe(true);
    });

    test("return false when recordId is undefined", () => {
      const criteria = new SimilarityCriteria();
      criteria.recordId = undefined;
      criteria.vectorName = "vectorName";
      criteria.limit = 50;
      criteria.order = "least";

      expect(criteria.isCompleted).toBe(false);
    });

    test("return false when vectorName is undefined", () => {
      const criteria = new SimilarityCriteria();
      criteria.recordId = "recordId";
      criteria.vectorName = undefined;
      criteria.limit = 50;
      criteria.order = "least";

      expect(criteria.isCompleted).toBe(false);
    });
  });

  describe("isEqual should", () => {
    test("return true when all criteria are equal", () => {
      const criteria = new SimilarityCriteria();
      criteria.recordId = "recordId";
      criteria.vectorName = "vectorName";
      criteria.limit = 50;
      criteria.order = "least";

      const other = new SimilarityCriteria();
      other.recordId = "recordId";
      other.vectorName = "vectorName";
      other.limit = 50;
      other.order = "least";

      expect(criteria.isEqual(other)).toBe(true);
    });

    test("return false when recordId is different", () => {
      const criteria = new SimilarityCriteria();
      criteria.recordId = "recordId";
      criteria.vectorName = "vectorName";
      criteria.limit = 50;
      criteria.order = "least";

      const other = new SimilarityCriteria();
      other.recordId = "otherRecordId";
      other.vectorName = "vectorName";
      other.limit = 50;
      other.order = "least";

      expect(criteria.isEqual(other)).toBe(false);
    });

    test("return false when vectorName is different", () => {
      const criteria = new SimilarityCriteria();
      criteria.recordId = "recordId";
      criteria.vectorName = "vectorName";
      criteria.limit = 50;
      criteria.order = "least";

      const other = new SimilarityCriteria();
      other.recordId = "recordId";
      other.vectorName = "otherVectorName";
      other.limit = 50;
      other.order = "least";

      expect(criteria.isEqual(other)).toBe(false);
    });

    test("return false when limit is different", () => {
      const criteria = new SimilarityCriteria();
      criteria.recordId = "recordId";
      criteria.vectorName = "vectorName";
      criteria.limit = 50;
      criteria.order = "least";

      const other = new SimilarityCriteria();
      other.recordId = "recordId";
      other.vectorName = "vectorName";
      other.limit = 100;
      other.order = "least";

      expect(criteria.isEqual(other)).toBe(false);
    });

    test("return false when order is different", () => {
      const criteria = new SimilarityCriteria();
      criteria.recordId = "recordId";
      criteria.vectorName = "vectorName";
      criteria.limit = 50;
      criteria.order = "least";

      const other = new SimilarityCriteria();
      other.recordId = "recordId";
      other.vectorName = "vectorName";
      other.limit = 50;
      other.order = "most";

      expect(criteria.isEqual(other)).toBe(false);
    });
  });

  describe("complete", () => {
    test("should set criteria values from urlParams", () => {
      const criteria = new SimilarityCriteria();
      criteria.complete(
        "record.cc74af18-8b40-4278-a527-83c38868e8f1.vector.mini-lm-sentence-transformers.limit.50.order.most"
      );

      expect(criteria.recordId).toBe("cc74af18-8b40-4278-a527-83c38868e8f1");
      expect(criteria.vectorName).toBe("mini-lm-sentence-transformers");
      expect(criteria.limit).toBe(50);
      expect(criteria.order).toBe("most");
    });
  });
});
