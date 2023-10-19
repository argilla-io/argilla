import { SimilarityCriteria } from "./SimilarityCriteria";

describe("SimilarityCriteria ", () => {
  describe("reset should", () => {
    test("set default criteria values", () => {
      const criteria = new SimilarityCriteria();
      criteria.complete("recordId", "vectorId", 50, "least");

      criteria.reset();

      expect(criteria.recordId).toBeUndefined();
      expect(criteria.vectorId).toBeUndefined();
      expect(criteria.limit).toBe(50);
      expect(criteria.order).toBe("most");
    });
  });

  describe("isCompleted should", () => {
    test("return true when all criteria are defined", () => {
      const criteria = new SimilarityCriteria();
      criteria.complete("recordId", "vectorId", 50, "least");

      expect(criteria.isCompleted).toBe(true);
    });

    test("return false when recordId is undefined", () => {
      const criteria = new SimilarityCriteria();
      criteria.complete(undefined, "vectorId", 50, "least");

      expect(criteria.isCompleted).toBe(false);
    });

    test("return false when vectorId is undefined", () => {
      const criteria = new SimilarityCriteria();
      criteria.complete("recordId", undefined, 50, "least");

      expect(criteria.isCompleted).toBe(false);
    });
  });

  describe("isEqual should", () => {
    test("return true when all criteria are equal", () => {
      const criteria = new SimilarityCriteria();
      criteria.complete("recordId", "vectorId", 50, "least");
      const other = new SimilarityCriteria();
      other.complete("recordId", "vectorId", 50, "least");

      expect(criteria.isEqual(other)).toBe(true);
    });

    test("return false when recordId is different", () => {
      const criteria = new SimilarityCriteria();
      criteria.complete("recordId", "vectorId", 50, "least");
      const other = new SimilarityCriteria();
      other.complete("otherRecordId", "vectorId", 50, "least");

      expect(criteria.isEqual(other)).toBe(false);
    });

    test("return false when vectorId is different", () => {
      const criteria = new SimilarityCriteria();
      criteria.complete("recordId", "vectorId", 50, "least");
      const other = new SimilarityCriteria();
      other.complete("recordId", "otherVectorId", 50, "least");

      expect(criteria.isEqual(other)).toBe(false);
    });

    test("return false when limit is different", () => {
      const criteria = new SimilarityCriteria();
      criteria.complete("recordId", "vectorId", 50, "least");
      const other = new SimilarityCriteria();
      other.complete("recordId", "vectorId", 100, "least");

      expect(criteria.isEqual(other)).toBe(false);
    });

    test("return false when order is different", () => {
      const criteria = new SimilarityCriteria();
      criteria.complete("recordId", "vectorId", 50, "least");
      const other = new SimilarityCriteria();
      other.complete("recordId", "vectorId", 50, "most");

      expect(criteria.isEqual(other)).toBe(false);
    });
  });
});
