import { Record } from "./Record";
import { RecordCriteria } from "./RecordCriteria";
import { Records } from "./Records";

describe("Records", () => {
  describe("getPageToFind", () => {
    test("current page should be from 1 to 10 when no have records", () => {
      const criteria = new RecordCriteria("1", 1, "pending", "", [], [], null);
      const records = new Records([]);

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 1, many: 10 });
    });

    test("next page should be from 10 and many 10 4when the user submit one record in current queue", () => {
      const criteria = new RecordCriteria("1", 10, "pending", "", [], [], null);
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

    test("previous page should be from 2 and many 1 when the user start with page 3 and go to backward", () => {
      const criteria = new RecordCriteria("1", 3, "pending", "", [], [], null);
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 3),
        new Record("2", "1", [], [], null, [], 1, 4),
      ]);
      criteria.page -= 1;

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 2, many: 1 });
    });

    test("the current page should be from 3 and many 50 when the user is filtering by similarity and no have records", () => {
      const criteria = new RecordCriteria(
        "1",
        3,
        "pending",
        "",
        [],
        [],
        // eslint-disable-next-line quotes
        '{"recordId":"1","vectorName":"2","limit":50,"order":"most"}'
      );
      const records = new Records([]);

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 3, many: 50 });
    });

    test("the current page should be from 2 and many 1 when the user is filtering by similarity but is going to backward", () => {
      const criteria = new RecordCriteria(
        "1",
        3,
        "pending",
        "",
        [],
        [],
        // eslint-disable-next-line quotes
        '{"recordId":"1","vectorName":"2","limit":50,"order":"most"}'
      );
      const records = new Records([
        new Record("1", "1", [], [], null, [], 1, 3),
        new Record("2", "1", [], [], null, [], 1, 4),
      ]);
      criteria.page -= 1;

      const pageToFind = records.getPageToFind(criteria);

      expect(pageToFind).toEqual({ from: 2, many: 1 });
    });
  });
});
