import { Record } from "./Record";
import { RecordCriteria } from "./RecordCriteria";
import { Records } from "./Records";

describe("Records", () => {
  describe("records order", () => {
    test("should ordered by page", () => {
      const firstRecord = new Record("1", "1", [], [], null, [], 1, 1);
      const secondRecord = new Record("2", "1", [], [], null, [], 1, 2);
      const records = new Records([secondRecord, firstRecord]);

      const first = records.records[0];

      expect(first).toEqual(firstRecord);
    });
  });

  describe("hasRecordsToAnnotate", () => {
    test("should return true when the records has records to annotate", () => {
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 1),
      ]);

      const hasRecordsToAnnotate = records.hasRecordsToAnnotate;

      expect(hasRecordsToAnnotate).toBeTruthy();
    });

    test("should return false when the records has not records to annotate", () => {
      const records = new Records([]);

      const hasRecordsToAnnotate = records.hasRecordsToAnnotate;

      expect(hasRecordsToAnnotate).toBeFalsy();
    });
  });

  describe("existsRecordOn", () => {
    test("should return true when the record exists", () => {
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 1),
      ]);

      const exists = records.existsRecordOn(1);

      expect(exists).toBeTruthy();
    });

    test("should return false when the record not exists in this page", () => {
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 2),
      ]);

      const exists = records.existsRecordOn(1);

      expect(exists).toBeFalsy();
    });
  });

  describe("getRecordOn", () => {
    test("should return the record when the record exists", () => {
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 1),
      ]);

      const record = records.getRecordOn(1);

      expect(record).toEqual(new Record("1", "1", [], [], null, [], 1, 1));
    });

    test("should return undefined when the record not exists in this page", () => {
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 2),
      ]);

      const record = records.getRecordOn(1);

      expect(record).toBeUndefined();
    });
  });

  describe("getById", () => {
    test("should return the record when the record exists", () => {
      const existingRecord = new Record("1", "1", [], [], null, [], 1, 1);
      const records = new Records([existingRecord]);

      const record = records.getById("1");

      expect(record).toEqual(existingRecord);
    });

    test("should return undefined when the record not exists", () => {
      const records = new Records([]);

      const record = records.getById("1");

      expect(record).toBeUndefined();
    });
  });

  describe("getPageToFind", () => {
    test("the current page should be from 1 to 10 when no have records", () => {
      const criteria = new RecordCriteria(
        "1",
        1,
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );
      const records = new Records([]);

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 1, many: 10 });
    });

    test("the page should be from 10 and many 10 when the user submit one record in current queue and going to forward", () => {
      const criteria = new RecordCriteria(
        "1",
        10,
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 1),
        new Record("2", "1", [], [], null, [], 1, 2),
        new Record("3", "1", [], [], null, [], 1, 3),
        new Record("4", "1", [], [], null, [], 1, 4),
        new Record("5", "1", [], [], null, [], 1, 5),
        new Record("6", "1", [], [], null, [], 1, 6),
        new Record("7", "1", [], [], null, [], 1, 7),
        new Record("8", "1", [], [], null, [], 1, 8),
        new Record("9", "1", [], [], null, [], 1, 9),
        new Record("10", "1", [], [], null, [], 1, 10),
      ]);
      records.records[0].submit({
        id: "1",
        value: "1",
        status: "submitted",
        updatedAt: "2021-01-01",
      });

      criteria.page += 1;

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 10, many: 10 });
    });

    test("the page should be from 9 and many 10 when the user submit two record in current queue and going to forward", () => {
      const criteria = new RecordCriteria(
        "1",
        10,
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 1),
        new Record("2", "1", [], [], null, [], 1, 2),
        new Record("3", "1", [], [], null, [], 1, 3),
        new Record("4", "1", [], [], null, [], 1, 4),
        new Record("5", "1", [], [], null, [], 1, 5),
        new Record("6", "1", [], [], null, [], 1, 6),
        new Record("7", "1", [], [], null, [], 1, 7),
        new Record("8", "1", [], [], null, [], 1, 8),
        new Record("9", "1", [], [], null, [], 1, 9),
        new Record("10", "1", [], [], null, [], 1, 10),
      ]);
      records.records[0].submit({
        id: "1",
        value: "1",
        status: "submitted",
        updatedAt: "2021-01-01",
      });
      records.records[1].submit({
        id: "2",
        value: "1",
        status: "submitted",
        updatedAt: "2021-01-01",
      });

      criteria.page += 1;

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 9, many: 10 });
    });

    test("the page should be from 2 and many 1 when the user start with page 3 and go to backward", () => {
      const criteria = new RecordCriteria(
        "1",
        3,
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 3),
        new Record("2", "1", [], [], null, [], 1, 4),
      ]);
      criteria.page -= 1;

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 2, many: 1 });
    });

    test("the current page should be from 1 and many 50 when the user is filtering by similarity", () => {
      const criteria = new RecordCriteria(
        "1",
        3,
        "pending",
        "",
        "",
        "",
        "",
        "",
        "record.1.vector.2.limit.50.order.most"
      );
      const records = new Records([]);

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 1, many: 50 });
    });

    test("the current page should be from 1 and many 50 when the user is filtering by similarity but is going to backward", () => {
      const criteria = new RecordCriteria(
        "1",
        3,
        "pending",
        "",
        "",
        "",
        "",
        "",
        "record.1.vector.2.limit.50.order.most"
      );
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 3),
        new Record("2", "1", [], [], null, [], 1, 4),
      ]);
      criteria.page -= 1;

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 1, many: 50 });
    });

    test("the current page should be from 9 and many 10 when the user is paginating fordward from page 8 and the queue has 8 records in draft but status is pending", () => {
      const criteria = new RecordCriteria(
        "1",
        9,
        "pending",
        "",
        "",
        "",
        "",
        "",
        ""
      );
      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          { status: "draft", id: "1", updatedAt: "", value: "" },
          [],
          1,
          1
        ),
        new Record(
          "2",
          "1",
          [],
          [],
          { status: "draft", id: "2", updatedAt: "", value: "" },
          [],
          1,
          2
        ),
        new Record(
          "3",
          "1",
          [],
          [],
          { status: "draft", id: "3", updatedAt: "", value: "" },
          [],
          1,
          3
        ),
        new Record(
          "4",
          "1",
          [],
          [],
          { status: "draft", id: "4", updatedAt: "", value: "" },
          [],
          1,
          4
        ),
        new Record(
          "5",
          "1",
          [],
          [],
          { status: "draft", id: "5", updatedAt: "", value: "" },
          [],
          1,
          5
        ),
        new Record(
          "6",
          "1",
          [],
          [],
          { status: "draft", id: "6", updatedAt: "", value: "" },
          [],
          1,
          6
        ),
        new Record(
          "7",
          "1",
          [],
          [],
          { status: "draft", id: "7", updatedAt: "", value: "" },
          [],
          1,
          7
        ),
        new Record(
          "8",
          "1",
          [],
          [],
          { status: "draft", id: "8", updatedAt: "", value: "" },
          [],
          1,
          8
        ),
      ]);

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 9, many: 10 });
    });
  });
});
