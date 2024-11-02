import { createBasicRecordCriteria } from "../__mocks__/criteria/mock";
import { PageCriteria } from "../page/PageCriteria";
import { SimilarityCriteria } from "../similarity/SimilarityCriteria";
import { Record } from "./Record";
import { RecordCriteria } from "./RecordCriteria";
import { EmptyQueueRecords, Records } from "./Records";

describe("Records", () => {
  describe("records order", () => {
    test("should ordered by page", () => {
      const firstRecord = new Record(
        "1",
        "1",
        [],
        [],
        null,
        [],
        1,
        1,
        {},
        "pending",
        new Date("2021-01-01"),
        new Date("2021-01-02")
      );
      const secondRecord = new Record(
        "2",
        "1",
        [],
        [],
        null,
        [],
        1,
        2,
        {},
        "pending",
        new Date("2021-01-01"),
        new Date("2021-01-02")
      );
      const records = new Records([secondRecord, firstRecord]);

      const first = records.records[0];

      expect(first).toEqual(firstRecord);
    });
  });

  describe("hasRecordsToAnnotate", () => {
    test("should return true when the records has records to annotate", () => {
      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          1,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
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
      const page = new PageCriteria();
      page.client = {
        page: 1,
        many: 10,
      };

      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          1,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      const exists = records.existsRecordOn(page);

      expect(exists).toBeTruthy();
    });

    test("should return false when the record not exists in this page", () => {
      const page = new PageCriteria();
      page.client = {
        page: 1,
        many: 10,
      };

      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          2,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      const exists = records.existsRecordOn(page);

      expect(exists).toBeFalsy();
    });
  });

  describe("getRecordOn", () => {
    test("should return the record when the record exists", () => {
      const page = new PageCriteria();
      page.client = {
        page: 1,
        many: 10,
      };

      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          1,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      const record = records.getRecordOn(page);

      expect(record).toEqual(
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          1,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        )
      );
    });

    test("should return undefined when the record not exists in this page", () => {
      const page = new PageCriteria();
      page.client = {
        page: 1,
        many: 10,
      };

      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          2,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      const record = records.getRecordOn(page);

      expect(record).toBeUndefined();
    });
  });

  describe("getById", () => {
    test("should return the record when the record exists", () => {
      const existingRecord = new Record(
        "1",
        "1",
        [],
        [],
        null,
        [],
        1,
        1,
        {},
        "pending",
        new Date("2021-01-01"),
        new Date("2021-01-02")
      );
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

  describe("synchronizePagination", () => {
    test("the current page should be from 1 to 10 when no have records", () => {
      const criteria = new RecordCriteria(
        "1",
        "1",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );
      const records = new Records([]);

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 1, many: 10 });
    });

    test("the page should be from 10 and many 10 when the user submit one record in current queue and going to forward", () => {
      const criteria = new RecordCriteria(
        "1",
        "10",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );
      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          1,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "2",
          "1",
          [],
          [],
          null,
          [],
          1,
          2,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "3",
          "1",
          [],
          [],
          null,
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "4",
          "1",
          [],
          [],
          null,
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "5",
          "1",
          [],
          [],
          null,
          [],
          1,
          5,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "6",
          "1",
          [],
          [],
          null,
          [],
          1,
          6,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "7",
          "1",
          [],
          [],
          null,
          [],
          1,
          7,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "8",
          "1",
          [],
          [],
          null,
          [],
          1,
          8,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "9",
          "1",
          [],
          [],
          null,
          [],
          1,
          9,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "10",
          "1",
          [],
          [],
          null,
          [],
          1,
          10,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);
      records.records[0].submit({
        id: "1",
        value: "1",
        status: "submitted",
        updatedAt: "2021-01-01",
      });

      criteria.nextPage();

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 10, many: 10 });
    });

    test("the page should be from 9 and many 10 when the user submit two record in current queue and going to forward", () => {
      const criteria = new RecordCriteria(
        "1",
        "10",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );
      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          1,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "2",
          "1",
          [],
          [],
          null,
          [],
          1,
          2,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "3",
          "1",
          [],
          [],
          null,
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "4",
          "1",
          [],
          [],
          null,
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "5",
          "1",
          [],
          [],
          null,
          [],
          1,
          5,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "6",
          "1",
          [],
          [],
          null,
          [],
          1,
          6,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "7",
          "1",
          [],
          [],
          null,
          [],
          1,
          7,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "8",
          "1",
          [],
          [],
          null,
          [],
          1,
          8,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "9",
          "1",
          [],
          [],
          null,
          [],
          1,
          9,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "10",
          "1",
          [],
          [],
          null,
          [],
          1,
          10,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
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

      criteria.nextPage();

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 9, many: 10 });
    });

    test("the page should be from 2 and many 1 when the user start with page 3 and go to backward", () => {
      const criteria = new RecordCriteria(
        "1",
        "3",
        "pending",
        "",
        "",
        "",
        "",
        "",
        null
      );
      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "2",
          "1",
          [],
          [],
          null,
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);
      criteria.previousPage();

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 2, many: 1 });
    });

    test("the current page should be from 1 and many 50 when the user is filtering by similarity", () => {
      const criteria = new RecordCriteria(
        "1",
        "3",
        "pending",
        "",
        "",
        "",
        "",
        "",
        "record.1.vector.2.limit.50.order.most"
      );
      const records = new Records([]);

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 1, many: 50 });
    });

    test("the current page should be from 1 and many 50 when the user is filtering by similarity but is going to backward", () => {
      const criteria = new RecordCriteria(
        "1",
        "3",
        "pending",
        "",
        "",
        "",
        "",
        "",
        "record.1.vector.2.limit.50.order.most"
      );
      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "2",
          "1",
          [],
          [],
          null,
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);
      criteria.previousPage();

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 1, many: 50 });
    });

    test("the current page should be from 1 and many 10 when the user is paginating forward from page 8 and the queue has 8 records in draft but status is pending", () => {
      const criteria = new RecordCriteria(
        "1",
        "9",
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
          1,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "2",
          "1",
          [],
          [],
          { status: "draft", id: "2", updatedAt: "", value: "" },
          [],
          1,
          2,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "3",
          "1",
          [],
          [],
          { status: "draft", id: "3", updatedAt: "", value: "" },
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "4",
          "1",
          [],
          [],
          { status: "draft", id: "4", updatedAt: "", value: "" },
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "5",
          "1",
          [],
          [],
          { status: "draft", id: "5", updatedAt: "", value: "" },
          [],
          1,
          5,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "6",
          "1",
          [],
          [],
          { status: "draft", id: "6", updatedAt: "", value: "" },
          [],
          1,
          6,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "7",
          "1",
          [],
          [],
          { status: "draft", id: "7", updatedAt: "", value: "" },
          [],
          1,
          7,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "8",
          "1",
          [],
          [],
          { status: "draft", id: "8", updatedAt: "", value: "" },
          [],
          1,
          8,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 1, many: 10 });
    });

    test("when the user is in bulk mode but was in focus mode the page should be from 1 and many 10", () => {
      const criteria = new RecordCriteria(
        "1",
        "5",
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
          null,
          [],
          1,
          5,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      criteria.page.bulkMode();

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 1, many: 10 });
    });

    test("when the user was in bulk mode but is in focus mode the page should be from 1 and many 10", () => {
      const criteria = new RecordCriteria(
        "1",
        "55",
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
          null,
          [],
          1,
          55,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      criteria.page.bulkMode();
      criteria.commit();

      criteria.page.focusMode();

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 1, many: 10 });
    });

    test("when the user was in bulk mode but is in focus mode the page should be from 1 and many 200 if the user is searching by similarity", () => {
      const criteria = new RecordCriteria(
        "1",
        "55",
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
          null,
          [],
          1,
          55,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      const similarityCriteria = new SimilarityCriteria();
      similarityCriteria.complete("record.1.vector.2.limit.200.order.most");

      criteria.page.bulkMode();
      criteria.similaritySearch.withValue(similarityCriteria);
      criteria.commit();

      criteria.page.focusMode();

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 1, many: 200 });
    });

    test("when te user is in bulk mode and is paginating backward the page should be from 1 and many 10 when the user is in page 11", () => {
      const criteria = new RecordCriteria(
        "1",
        "11",
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
          null,
          [],
          1,
          11,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      criteria.page.bulkMode();
      criteria.commit();
      criteria.previousPage();

      records.synchronizeQueuePagination(criteria);

      expect(criteria.page.server).toEqual({ from: 1, many: 10 });
    });
  });

  describe("append", () => {
    test("should append the new records to the current records when not exists", () => {
      const records = new Records([
        new Record(
          "2",
          "1",
          [],
          [],
          null,
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);
      const newRecords = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      records.append(newRecords);

      expect(records.records).toEqual([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "2",
          "1",
          [],
          [],
          null,
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);
    });

    test("should replace the new records to the current records when exists and never change the total", () => {
      const records = new Records(
        [
          new Record(
            "2",
            "1",
            [],
            [],
            null,
            [],
            1,
            4,
            {},
            "pending",
            new Date("2021-01-01"),
            new Date("2021-01-01")
          ),
        ],
        200
      );

      const newRecords = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "2",
          "REPLACED",
          [],
          [],
          null,
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);

      records.append(newRecords);

      expect(records.records).toEqual([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
        new Record(
          "2",
          "REPLACED",
          [],
          [],
          null,
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-02")
        ),
      ]);
      expect(records.total).toBe(200);
    });
  });

  describe("hasNecessaryBuffering", () => {
    test("should return false when the buffer has at least 50% extra records loaded", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.client = {
        page: 1,
        many: 4,
      };

      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          1,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-01")
        ),
        new Record(
          "2",
          "1",
          [],
          [],
          null,
          [],
          1,
          2,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-01")
        ),
        new Record(
          "3",
          "1",
          [],
          [],
          null,
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-01")
        ),
        new Record(
          "4",
          "1",
          [],
          [],
          null,
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-01")
        ),
      ]);

      const shouldBuffering = records.shouldBuffering(pageCriteria);

      expect(shouldBuffering).toBeFalsy();
    });

    test("should return true when the buffer no have at least 50% extra records loaded", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.client = {
        page: 1,
        many: 10,
      };

      const records = new Records([
        new Record(
          "1",
          "1",
          [],
          [],
          null,
          [],
          1,
          1,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-01")
        ),
        new Record(
          "2",
          "1",
          [],
          [],
          null,
          [],
          1,
          2,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-01")
        ),
        new Record(
          "3",
          "1",
          [],
          [],
          null,
          [],
          1,
          3,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-01")
        ),
        new Record(
          "4",
          "1",
          [],
          [],
          null,
          [],
          1,
          4,
          {},
          "pending",
          new Date("2021-01-01"),
          new Date("2021-01-01")
        ),
      ]);

      const shouldBuffering = records.shouldBuffering(pageCriteria);

      expect(shouldBuffering).toBeTruthy();
    });

    test("should return false when is end of the queue", () => {
      const pageCriteria = new PageCriteria();
      pageCriteria.client = {
        page: 100,
        many: 4,
      };

      const records = new Records(
        [
          new Record(
            "4",
            "1",
            [],
            [],
            null,
            [],
            1,
            100,
            {},
            "pending",
            new Date("2021-01-01"),
            new Date("2021-01-01")
          ),
        ],
        100
      );

      const shouldBuffering = records.shouldBuffering(pageCriteria);

      expect(shouldBuffering).toBeFalsy();
    });
  });
});

describe("EmptyQueueRecords", () => {
  describe("hasRecordsToAnnotate", () => {
    test("should be false always", () => {
      const records = new EmptyQueueRecords(createBasicRecordCriteria(), []);

      const hasRecordsToAnnotate = records.hasRecordsToAnnotate;

      expect(hasRecordsToAnnotate).toBeFalsy();
    });
  });

  describe("getRecordOn", () => {
    test("always should return the record configured by record criteria", () => {
      const recordCriteria = createBasicRecordCriteria();
      const records = new EmptyQueueRecords(recordCriteria, []);

      const hasRecordsToAnnotate = records.getRecordOn(recordCriteria.page);

      expect(hasRecordsToAnnotate).toBeTruthy();
    });
  });
});
